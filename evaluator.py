import sqlite3
import time
import tempfile
from pathlib import Path
import json

class SQLEvaluator:
    def __init__(self, test_db_path="data/test.db"):
        self.test_db_path = test_db_path

    def evaluate_query(self, 
                       schema: str, 
                       original_query: str, 
                       optimized_query: str,
                       num_runs: int = 5) -> dict:

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db_file:
            temp_db = temp_db_file.name

        try:
            conn = sqlite3.connect(temp_db)
            conn.executescript(schema)

            if Path(self.test_db_path).exists():
                self._copy_data(conn)

            original_result, original_time = self._run_query(conn, original_query, num_runs)

            if original_result is None:
                return {"success": False, "reward": 0, "error": "Original query failed"}
            
            optimized_result, optimized_time = self._run_query(conn, optimized_query, num_runs)

            if optimized_result is None:
                return {"success": False, "reward": 0, "error": "Optimized query failed"}
            
            results_match = self._results_equal(original_result, optimized_result)

            if not results_match:
                return {"success": False, "reward": 0, "error": "Results do not match"}
            
            if optimized_time == 0:
                speedup = 1.0
            else:
                speedup = original_time / optimized_time

            if speedup >= 1.1:  # At least 10% faster
                reward = min(speedup / 10.0, 1.0)  # Normalize to 0-1
            elif speedup > 0.95:  # Similar performance is ok
                reward = 0.5
            else:  # Slower = bad
                reward = 0
            
            conn.close()

            return {
                "success": True,
                "reward": reward,
                "original_time": original_time,
                "optimized_time": optimized_time,
                "speedup": speedup,
                "results_match": True
            }
        except Exception as e:
            return {"success": False, "reward": 0, "error": str(e)}
        finally:
            if Path(temp_db).exists():
                Path(temp_db).unlink(missing_ok=True)


    def _run_query(self, conn, query: str, num_runs: int):
        try:
            result = conn.execute(query).fetchall()
            times = []
            for _ in range(num_runs):
                start_time = time.perf_counter()
                conn.execute(query).fetchall()
                times.append(time.perf_counter() - start_time)

            avg_time = sum(times) / num_runs
            return result, avg_time
        except Exception as e:
            return None, None
        
    def _results_equal(self, result1, result2) -> bool:
        if len(result1) != len(result2):
            return False
        
        sorted1 = sorted([tuple(row) for row in result1])
        sorted2 = sorted([tuple(row) for row in result2])
        
        return sorted1 == sorted2
    
    def _copy_data(self, conn):
        source = sqlite3.connect(self.test_db_path)
        tables = source.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for (table_name,) in tables:
            data = source.execute(f"SELECT * FROM {table_name}").fetchall()
            
            if data:
                placeholders = ','.join(['?'] * len(data[0]))
                conn.executemany(
                    f"INSERT INTO {table_name} VALUES ({placeholders})",
                    data
                )

        conn.commit()
        source.close()


if __name__ == "__main__":
    evaluator = SQLEvaluator()
    
    result = evaluator.evaluate_query(
        schema="""
CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);
INSERT INTO users VALUES (1, 'Alice', 30);
INSERT INTO users VALUES (2, 'Bob', 25);
INSERT INTO users VALUES (3, 'Charlie', 35);
""",
        original_query="SELECT * FROM users WHERE age > 25;",
        optimized_query="""
CREATE INDEX idx_age ON users(age);
SELECT * FROM users WHERE age > 25;
""",
        num_runs=10
    )
    
    print(json.dumps(result, indent=2))