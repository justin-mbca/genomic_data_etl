# Genomics Data Engineering Prototype

This project demonstrates a free-tier AWS genomics data engineering pipeline using Python, AWS CDK, Lambda, S3, Step Functions, and DynamoDB.

## 🗺️ Architecture Overview (Mermaid Diagram)

```mermaid
flowchart TD
	UPL["Researchers<br>Lab Technicians<br>Bioinformaticians"]
	UI["Web UI / CLI / API"]
	SENG["<b>Senior Genomic Data Engineer</b><br>Designs, reviews, optimizes<br>all infrastructure & code"]

	subgraph S3["S3 Buckets"]
		RAW["raw-genomics-bucket<br>(VCF, CRAM)"]
		PROCESSED["processed-genomics-bucket<br>(VCF.gz, QC reports)"]
		DELIVERY["delivery-bucket<br>(Partner Data)"]
	end

	subgraph Lambda["Lambda Functions"]
		VALIDATE["validation-handler<br>(VCF/CRAM validation)<br><br><b>Bioinformatics Engineers</b>"]
		PROCESS["vcf-processor<br>(Variant processing)<br><br><b>Bioinformaticians<br>Data Scientists</b>"]
		METRICS["quality-metrics<br>(QC metrics)<br><br><b>Bioinformaticians<br>Data Scientists</b>"]
		METAUPD["metadata-updater<br>(DynamoDB updates)<br><br><b>Data Stewards</b>"]
	end

	subgraph DDB["DynamoDB Tables"]
		META["genomics-metadata<br>(sample_id, file metadata)<br><br><b>Project Managers<br>Data Stewards<br>Researchers</b>"]
		JOBS["processing-jobs<br>(job_id, status)<br><br><b>Pipeline Operators<br>DevOps</b>"]
		QC["quality-metrics<br>(sample_id, QC results)<br><br><b>Bioinformaticians<br>Researchers</b>"]
	end

	subgraph SFN["Step Functions Workflow"]
		WORKFLOW["Genomics State Machine<br><br><b>Pipeline Operators<br>DevOps</b>"]
	end

	subgraph EXT["External"]
		PARTNERS["External Partners<br>Collaborators<br>Data Consumers"]
	end

	%% User Interactions
	UPL -->|"Upload VCF/CRAM"| UI
	UI -->|"Upload to S3"| RAW
	UI -->|"Trigger Workflow"| WORKFLOW
	UI <-->|"View Results / Download"| DELIVERY
	UI <-->|"Check Status / QC"| META
	UI <-->|"Check Status / QC"| QC
	PARTNERS <-->|"Download Delivery Data"| DELIVERY

	%% Senior Genomic Data Engineer Interactions
	SENG -.-> RAW
	SENG -.-> PROCESSED
	SENG -.-> DELIVERY
	SENG -.-> VALIDATE
	SENG -.-> PROCESS
	SENG -.-> METRICS
	SENG -.-> METAUPD
	SENG -.-> META
	SENG -.-> JOBS
	SENG -.-> QC
	SENG -.-> WORKFLOW

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
