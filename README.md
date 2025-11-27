# Genomics Data Engineering Prototype

This project demonstrates a free-tier AWS genomics data engineering pipeline using Python, AWS CDK, Lambda, S3, Step Functions, and DynamoDB.

## 🗺️ Architecture Overview (Mermaid Diagram)

```mermaid
flowchart TD
	subgraph S3["S3 Buckets"]
		RAW["raw-genomics-bucket (VCF, CRAM)"]
		PROCESSED["processed-genomics-bucket (VCF.gz, QC reports)"]
		DELIVERY["delivery-bucket (Partner Data)"]
	end

	subgraph Lambda["Lambda Functions"]
		VALIDATE["validation-handler\n(VCF/CRAM validation)"]
		PROCESS["vcf-processor\n(Variant processing)"]
		METRICS["quality-metrics\n(QC metrics)"]
		METAUPD["metadata-updater\n(DynamoDB updates)"]
	end

	subgraph DDB["DynamoDB Tables"]
		META["genomics-metadata\n(sample_id, file metadata)"]
		JOBS["processing-jobs\n(job_id, status)"]
		QC["quality-metrics\n(sample_id, QC results)"]
	end

	subgraph SFN["Step Functions Workflow"]
		WORKFLOW["Genomics State Machine"]
	end

	RAW --> VALIDATE
	VALIDATE --> META
	VALIDATE --> WORKFLOW
	WORKFLOW --> PROCESS
	PROCESS --> PROCESSED
	PROCESS --> JOBS
	PROCESS --> METRICS
	METRICS --> QC
	PROCESSED --> DELIVERY
	WORKFLOW --> METAUPD
	METAUPD --> META
	WORKFLOW --> METRICS

	%% Data Types
	classDef dataType fill:#f9f,stroke:#333,stroke-width:1px;
	VCF["VCF"]:::dataType
	CRAM["CRAM"]:::dataType
	QC_METRICS["QC Metrics"]:::dataType
	VCF_GZ["VCF.gz"]:::dataType

	RAW -.-> VCF
	RAW -.-> CRAM
	PROCESSED -.-> VCF_GZ
	PROCESSED -.-> QC_METRICS
```
