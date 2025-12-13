import sqlite3
import time
import tempfile
from pathlib import Path
import json

class SQLEvaluator:
    def __init__(self, test_db_path="data/test.db", use_readability_judge=False):
        self.test_db_path = test_db_path
        self.use_readability_judge = use_readability_judge
        self.readability_judge = None

        if use_readability_judge:
            from quill.llm_judge import SQLReadabilityJudge
            self.readability_judge = SQLReadabilityJudge()

    def evaluate_query(self,
                       schema: str,
                       original_query: str,
                       optimized_query: str,
                       num_runs: int = 5,
                       timeout_seconds: int = 30) -> dict:

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db_file:
            temp_db = temp_db_file.name

        try:
            conn = sqlite3.connect(temp_db)
            conn.executescript(schema)

            if Path(self.test_db_path).exists():
                self._copy_data(conn)

            original_result, original_time = self._run_query(conn, original_query, num_runs, timeout_seconds)

            # If original query timed out, use timeout as max time
            original_timed_out = False
            if original_result is None:
                original_timed_out = True
                original_time = timeout_seconds

            optimized_result, optimized_time = self._run_query(conn, optimized_query, num_runs, timeout_seconds)

            if optimized_result is None:
                return {"success": False, "reward": 0, "error": "Optimized query failed or timed out"}

            # If original timed out, we can't verify correctness, so skip the check
            if not original_timed_out:
                results_match = self._results_equal(original_result, optimized_result)
                if not results_match:
                    return {"success": False, "reward": 0, "error": "Results do not match"}
            
            if optimized_time == 0:
                speedup = 1.0
            else:
                speedup = original_time / optimized_time

            if speedup >= 1.1:
                reward = min(speedup / 10.0, 1.0)
            elif speedup > 0.95:
                reward = 0.5
            else:
                reward = 0

            readability_bonus = 0.0
            readability_preference = None
            readability_reasoning = None

            if self.use_readability_judge and self.readability_judge:
                try:
                    judge_result = self.readability_judge.judge_readability(
                        query_a=original_query,
                        query_b=optimized_query,
                        schema=schema
                    )
                    readability_preference = judge_result.get("preference")
                    readability_reasoning = judge_result.get("reasoning")
                    confidence = judge_result.get("confidence", "medium")
                    readability_bonus = self.readability_judge.calculate_readability_bonus(
                        readability_preference,
                        confidence
                    )
                    reward = max(0, min(1.0, reward + readability_bonus))
                except Exception as e:
                    print(f"Readability judge error: {e}")

            conn.close()

            result = {
                "success": True,
                "reward": reward,
                "original_time": original_time,
                "optimized_time": optimized_time,
                "speedup": speedup,
                "results_match": not original_timed_out,
                "original_timed_out": original_timed_out
            }

            if self.use_readability_judge:
                result["readability_preference"] = readability_preference
                result["readability_reasoning"] = readability_reasoning
                result["readability_bonus"] = readability_bonus

            return result
        except Exception as e:
            return {"success": False, "reward": 0, "error": str(e)}
        finally:
            if Path(temp_db).exists():
                Path(temp_db).unlink(missing_ok=True)


    def _run_query(self, conn, query: str, num_runs: int, timeout_seconds: int = 30):
        try:
            # Split query into statements
            statements = [s.strip() for s in query.strip().split(';') if s.strip()]

            # Execute all DDL statements (CREATE, ALTER, DROP) first without timing
            select_statement = None
            for stmt in statements:
                stmt_upper = stmt.upper().lstrip()
                if stmt_upper.startswith('SELECT'):
                    select_statement = stmt
                else:
                    # Execute DDL/DML statements (CREATE INDEX, etc.)
                    conn.execute(stmt)

            # If no SELECT found, assume the last statement is the query to time
            if select_statement is None:
                select_statement = statements[-1]

            # Set a timeout for the connection
            conn.execute(f"PRAGMA busy_timeout = {timeout_seconds * 1000}")

            # Get result once with timeout check
            start = time.perf_counter()
            result = conn.execute(select_statement).fetchall()
            if time.perf_counter() - start > timeout_seconds:
                return None, None

            # Time the SELECT query only
            times = []
            for _ in range(num_runs):
                start_time = time.perf_counter()
                conn.execute(select_statement).fetchall()
                elapsed = time.perf_counter() - start_time

                # Check if this single run exceeded timeout
                if elapsed > timeout_seconds:
                    return None, None

                times.append(elapsed)

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

        # Get tables from source database
        source_tables = source.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        # Get tables from destination database
        dest_tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        dest_table_names = {name for (name,) in dest_tables}

        # Only copy tables that exist in both databases
        for (table_name,) in source_tables:
            if table_name not in dest_table_names:
                continue  # Skip tables that don't exist in destination

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