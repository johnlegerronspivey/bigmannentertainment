"""AWS Athena Service - Interactive S3 log analytics."""
import os
import logging
import time
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AthenaService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        self.output_location = f"s3://{os.environ.get('S3_BUCKET_NAME', 'bigmann-entertainment-media')}/athena-results/"

        try:
            self._client = boto3.client(
                "athena",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_work_groups(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Athena init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {
            "available": True,
            "region": self.region,
            "service": "AWS Athena",
            "output_location": self.output_location,
        }

    def list_work_groups(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.list_work_groups(MaxResults=50)
        return [
            {
                "name": wg.get("Name", ""),
                "state": wg.get("State", ""),
                "description": wg.get("Description", ""),
                "engine_version": wg.get("EngineVersion", {}).get("SelectedEngineVersion", ""),
            }
            for wg in resp.get("WorkGroups", [])
        ]

    def list_databases(self, catalog: str = "AwsDataCatalog") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.list_databases(CatalogName=catalog, MaxResults=50)
        return [
            {
                "name": db.get("Name", ""),
                "description": db.get("Description", ""),
                "parameters": db.get("Parameters", {}),
            }
            for db in resp.get("DatabaseList", [])
        ]

    def list_table_metadata(self, catalog: str, database: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.list_table_metadata(
            CatalogName=catalog, DatabaseName=database, MaxResults=50
        )
        return [
            {
                "name": t.get("Name", ""),
                "type": t.get("TableType", ""),
                "columns": [
                    {"name": c.get("Name", ""), "type": c.get("Type", "")}
                    for c in t.get("Columns", [])
                ],
                "partition_keys": [
                    {"name": p.get("Name", ""), "type": p.get("Type", "")}
                    for p in t.get("PartitionKeys", [])
                ],
                "created_at": t.get("CreateTime", "").isoformat() if t.get("CreateTime") else "",
            }
            for t in resp.get("TableMetadataList", [])
        ]

    def list_named_queries(self, work_group: str = "primary") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.list_named_queries(WorkGroup=work_group, MaxResults=50)
        query_ids = resp.get("NamedQueryIds", [])
        if not query_ids:
            return []
        batch = self._client.batch_get_named_query(NamedQueryIds=query_ids[:50])
        return [
            {
                "id": q.get("NamedQueryId", ""),
                "name": q.get("Name", ""),
                "database": q.get("Database", ""),
                "query": q.get("QueryString", ""),
                "description": q.get("Description", ""),
                "work_group": q.get("WorkGroup", ""),
            }
            for q in batch.get("NamedQueries", [])
        ]

    def start_query(self, query: str, database: str = "default",
                    work_group: str = "primary") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={"OutputLocation": self.output_location},
            WorkGroup=work_group,
        )
        return {"query_execution_id": resp.get("QueryExecutionId", "")}

    def get_query_status(self, execution_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.get_query_execution(QueryExecutionId=execution_id)
        ex = resp.get("QueryExecution", {})
        status = ex.get("Status", {})
        stats = ex.get("Statistics", {})
        return {
            "execution_id": ex.get("QueryExecutionId", ""),
            "query": ex.get("Query", ""),
            "state": status.get("State", ""),
            "reason": status.get("StateChangeReason", ""),
            "submitted_at": status.get("SubmissionDateTime", "").isoformat() if status.get("SubmissionDateTime") else "",
            "completed_at": status.get("CompletionDateTime", "").isoformat() if status.get("CompletionDateTime") else "",
            "data_scanned_bytes": stats.get("DataScannedInBytes", 0),
            "execution_time_ms": stats.get("EngineExecutionTimeInMillis", 0),
            "output_location": ex.get("ResultConfiguration", {}).get("OutputLocation", ""),
        }

    def get_query_results(self, execution_id: str, max_results: int = 100) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.get_query_results(
            QueryExecutionId=execution_id, MaxResults=max_results
        )
        columns = [
            c.get("Label", c.get("Name", ""))
            for c in resp.get("ResultSet", {}).get("ResultSetMetadata", {}).get("ColumnInfo", [])
        ]
        rows_raw = resp.get("ResultSet", {}).get("Rows", [])
        rows = []
        for row in rows_raw[1:]:  # skip header row
            values = [d.get("VarCharValue", "") for d in row.get("Data", [])]
            rows.append(dict(zip(columns, values)))
        return {"columns": columns, "rows": rows, "total": len(rows)}

    def list_query_executions(self, work_group: str = "primary", max_results: int = 20) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Athena not available")
        resp = self._client.list_query_executions(WorkGroup=work_group, MaxResults=max_results)
        exec_ids = resp.get("QueryExecutionIds", [])
        if not exec_ids:
            return []
        batch = self._client.batch_get_query_execution(QueryExecutionIds=exec_ids[:20])
        results = []
        for ex in batch.get("QueryExecutions", []):
            status = ex.get("Status", {})
            results.append({
                "execution_id": ex.get("QueryExecutionId", ""),
                "query": (ex.get("Query", "")[:100] + "...") if len(ex.get("Query", "")) > 100 else ex.get("Query", ""),
                "state": status.get("State", ""),
                "submitted_at": status.get("SubmissionDateTime", "").isoformat() if status.get("SubmissionDateTime") else "",
                "data_scanned_bytes": ex.get("Statistics", {}).get("DataScannedInBytes", 0),
            })
        return results
