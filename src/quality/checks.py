"""Data quality check functions"""
import pandas as pd
from typing import Dict, List
from src.db.queries import save_quality_metric, save_quality_issue

def check_completeness(df: pd.DataFrame, table_name: str, source: str = None) -> Dict[str, float]:
    """Check completeness (non-null percentage) for each column"""
    completeness_metrics = {}
    
    for column in df.columns:
        non_null_count = df[column].notna().sum()
        total_count = len(df)
        completeness_pct = (non_null_count / total_count) * 100 if total_count > 0 else 0
        
        completeness_metrics[column] = completeness_pct
        
        # Save to database
        save_quality_metric(
            table_name=table_name,
            column_name=column,
            metric_type='completeness',
            metric_value=completeness_pct,
            source=source
        )
        
        print(f"  {column}: {completeness_pct:.2f}% complete")
        
        # Log issues for columns with low completeness
        if completeness_pct < 90:
            save_quality_issue(
                table_name=table_name,
                row_id=None,
                issue_type='low_completeness',
                issue_description=f"Column {column} is only {completeness_pct:.2f}% complete",
                severity='medium' if completeness_pct >= 80 else 'high',
                source=source
            )
    
    return completeness_metrics

def check_format_conformity(df: pd.DataFrame, table_name: str, 
                           column_rules: Dict[str, str], source: str = None) -> Dict[str, float]:
    """Check format conformity based on regex patterns"""
    conformity_metrics = {}
    
    for column, pattern in column_rules.items():
        if column not in df.columns:
            continue
        
        # Only check non-null values
        non_null_series = df[column].dropna()
        
        if len(non_null_series) == 0:
            conformity_metrics[column] = 0.0
            continue
        
        # Check pattern match
        matching_count = non_null_series.astype(str).str.match(pattern).sum()
        conformity_pct = (matching_count / len(non_null_series)) * 100
        
        conformity_metrics[column] = conformity_pct
        
        # Save to database
        save_quality_metric(
            table_name=table_name,
            column_name=column,
            metric_type='format_conformity',
            metric_value=conformity_pct,
            source=source
        )
        
        print(f"  {column}: {conformity_pct:.2f}% conform to pattern")
        
        # Log non-conforming values
        if conformity_pct < 95:
            non_conforming = non_null_series[~non_null_series.astype(str).str.match(pattern)]
            for idx, value in non_conforming.head(5).items():  # Log first 5
                save_quality_issue(
                    table_name=table_name,
                    row_id=str(df.loc[idx, 'ID']) if 'ID' in df.columns else str(idx),
                    issue_type='format_violation',
                    issue_description=f"Column {column} has invalid format: '{value}'",
                    severity='low',
                    source=source
                )
    
    return conformity_metrics

def check_duplicates(df: pd.DataFrame, table_name: str, 
                    id_column: str = 'ID', source: str = None) -> int:
    """Check for duplicate IDs"""
    if id_column not in df.columns:
        print(f"  ⚠️  ID column '{id_column}' not found")
        return 0
    
    duplicate_count = df[id_column].duplicated().sum()
    total_count = len(df)
    duplicate_pct = (duplicate_count / total_count) * 100 if total_count > 0 else 0
    
    # Save metric
    save_quality_metric(
        table_name=table_name,
        column_name=id_column,
        metric_type='duplicates',
        metric_value=duplicate_pct,
        source=source
    )
    
    print(f"  {duplicate_count} duplicate IDs found ({duplicate_pct:.2f}%)")
    
    # Log duplicate issues
    if duplicate_count > 0:
        duplicates = df[df[id_column].duplicated(keep=False)]
        for dup_id in duplicates[id_column].unique()[:5]:  # Log first 5
            save_quality_issue(
                table_name=table_name,
                row_id=str(dup_id),
                issue_type='duplicate',
                issue_description=f"Duplicate ID found: {dup_id}",
                severity='high',
                source=source
            )
    
    return duplicate_count

def run_quality_checks(df: pd.DataFrame, table_name: str, source: str = None):
    """Run all quality checks on a dataframe"""
    print(f"\n🔍 Running quality checks on {table_name}...")
    
    # Completeness check
    print("\n📊 Completeness Check:")
    completeness = check_completeness(df, table_name, source)
    
    # Format conformity check
    print("\n📋 Format Conformity Check:")
    format_rules = {
        'ID': r'^P\d{4}$',  # Pattern: P followed by 4 digits
        'CSP': r'^\d{1,2}$',  # Pattern: 1 or 2 digits
    }
    conformity = check_format_conformity(df, table_name, format_rules, source)
    
    # Duplicate check
    print("\n🔄 Duplicate Check:")
    duplicates = check_duplicates(df, table_name, 'ID', source)
    
    print(f"\n✅ Quality checks complete for {table_name}")
    
    return {
        'completeness': completeness,
        'conformity': conformity,
        'duplicates': duplicates
    }