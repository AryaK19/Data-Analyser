import ast
import time
import sys
import traceback
import tracemalloc
from typing import Dict, Any
import pandas as pd
import numpy as np

def count_operations(node: ast.AST) -> int:
    """Count the number of operations in AST to estimate time complexity"""
    operations = 0
    
    # Count loops
    if isinstance(node, (ast.For, ast.While)):
        operations += 10  # Base cost for loop
        
    # Count nested loops
    elif isinstance(node, ast.ListComp):
        operations += 5 * len(node.generators)
        
    # Count function calls
    elif isinstance(node, ast.Call):
        operations += 1
        
    # Count operations
    elif isinstance(node, (ast.BinOp, ast.Compare, ast.BoolOp)):
        operations += 1
        
    # Recursively process all child nodes
    for child in ast.iter_child_nodes(node):
        operations += count_operations(child)
    
    return operations

def measure_execution_time(code: str, sample_size: int = 5) -> float:
    """Measure average execution time"""
    times = []
    namespace = {}
    
    for _ in range(sample_size):
        start_time = time.perf_counter()
        exec(code, namespace)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return sum(times) / len(times)

def measure_memory_usage(code: str) -> int:
    """Measure peak memory usage"""
    tracemalloc.start()
    namespace = {}
    exec(code, namespace)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak



def estimate_complexity(operations: int) -> str:
    """Estimate big O notation based on operation count"""
    if operations <= 5:
        return "O(1)"
    elif operations <= 15:
        return "O(log n)"
    elif operations <= 30:
        return "O(n)"
    elif operations <= 50:
        return "O(n log n)"
    else:
        return "O(n²)"
    


def execute_code_safely(code: str, df: pd.DataFrame) -> Any:
    """Execute code safely with proper context"""
    try:
        # Create namespace with required imports and context
        namespace = {
            'df': df,
            'pd': pd,
            'np': np,
            'result': None
        }
        
        # Clean and execute code
        clean_code = '\n'.join(
            line for line in code.split('\n')
            if line.strip() and not line.strip().startswith('#')
        )
        exec(clean_code, namespace)
        return namespace.get('result')
        
    except Exception as e:
        raise RuntimeError(f"Error executing code: {str(e)}")

def measure_execution_time(code: str, df: pd.DataFrame, sample_size: int = 5) -> float:
    """Measure average execution time"""
    times = []
    
    for _ in range(sample_size):
        start_time = time.perf_counter()
        try:
            execute_code_safely(code, df)
        except Exception as e:
            raise RuntimeError(f"Error measuring execution time: {str(e)}")
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    return sum(times) / len(times)

def measure_memory_usage(code: str, df: pd.DataFrame) -> int:
    """Measure peak memory usage"""
    tracemalloc.start()
    try:
        execute_code_safely(code, df)
        current, peak = tracemalloc.get_traced_memory()
        return peak
    finally:
        tracemalloc.stop()

def is_efficient(generated_code: str, test_code: str = None, df: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Analyze and compare efficiency of generated code vs test code
    Returns dictionary with analysis results
    """
    try:
        if df is None:
            raise ValueError("DataFrame is required for efficiency analysis")

        # Parse AST for generated code
        generated_ast = ast.parse(generated_code)
        generated_ops = count_operations(generated_ast)
        generated_complexity = estimate_complexity(generated_ops)
        
        # Measure execution metrics for generated code
        generated_time = measure_execution_time(generated_code, df)
        generated_memory = measure_memory_usage(generated_code, df)
        
        results = {
            "generated_code": {
                "time_complexity": generated_complexity,
                "execution_time": f"{generated_time:.6f} sec",
                "memory_usage": f"{generated_memory / 1024:.2f} KB",
                "operation_count": generated_ops
            },
            "comparison": {
                "is_efficient": True,
                "notes": []
            }
        }
        
        # Compare with test code if provided
        if test_code:
            test_ast = ast.parse(test_code)
            test_ops = count_operations(test_ast)
            test_complexity = estimate_complexity(test_ops)
            test_time = measure_execution_time(test_code, df)
            test_memory = measure_memory_usage(test_code, df)
            
            results["test_code"] = {
                "time_complexity": test_complexity,
                "execution_time": f"{test_time:.6f} seconds",
                "memory_usage": f"{test_memory / 1024:.2f} KB",
                "operation_count": test_ops
            }
            
            # Compare and add notes
            if generated_ops > test_ops*2 :
                results["comparison"]["is_efficient"] = False
                results["comparison"]["notes"].append(
                    "Generated code has significantly more operations"
                )
            
            if generated_time > test_time*2 :
                results["comparison"]["is_efficient"] = False
                results["comparison"]["notes"].append(
                    "Generated code is significantly slower"
                )
            
            if generated_memory > test_memory*2 :
                results["comparison"]["is_efficient"] = False
                results["comparison"]["notes"].append(
                    "Generated code uses significantly more memory"
                )
        
        return results
        
    except Exception as e:
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }