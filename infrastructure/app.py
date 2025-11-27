
import os

LOCAL_MODE = os.getenv("LOCAL_MODE", "0") == "1"

if LOCAL_MODE:
	print("[INFO] Running in LOCAL_MODE: Skipping AWS CDK stack creation and deployment.")

	# --- Local Mock Classes ---
	class MockS3:
		def __init__(self):
			self.buckets = {}
		def create_bucket(self, name):
			self.buckets[name] = {}
			print(f"[MOCK S3] Created bucket: {name}")
		def put_object(self, bucket, key, data):
			self.buckets.setdefault(bucket, {})[key] = data
			print(f"[MOCK S3] Put object: {key} in {bucket}")
		def get_object(self, bucket, key):
			return self.buckets.get(bucket, {}).get(key)

	class MockDynamoDB:
		def __init__(self):
			self.tables = {}
		def create_table(self, name):
			self.tables[name] = []
			print(f"[MOCK DynamoDB] Created table: {name}")
		def put_item(self, table, item):
			self.tables.setdefault(table, []).append(item)
			print(f"[MOCK DynamoDB] Put item in {table}: {item}")
		def scan(self, table):
			return self.tables.get(table, [])

	class MockLambda:
		def __init__(self):
			self.functions = {}
		def create_function(self, name, handler):
			self.functions[name] = handler
			print(f"[MOCK Lambda] Created function: {name}")
		def invoke(self, name, event):
			if name in self.functions:
				print(f"[MOCK Lambda] Invoking {name} with event: {event}")
				return self.functions[name](event)
			else:
				print(f"[MOCK Lambda] No such function: {name}")

	class MockStepFunctions:
		def __init__(self):
			self.state_machines = {}
		def create_state_machine(self, name, definition):
			self.state_machines[name] = definition
			print(f"[MOCK StepFunctions] Created state machine: {name}")
		def start_execution(self, name, input):
			print(f"[MOCK StepFunctions] Executing {name} with input: {input}")
			# Simulate execution
			return {"status": "SUCCEEDED", "input": input}

	# Sample genomics input data
	sample_fastq = "@SEQ_ID\nGATTTGGGGTTTAAAGGG...\n+\n!''*((((***+))%%%++)(%%%%).1***-+*''))**55CCF>>>>>>CCCCCCC65"
	sample_bam = b"BAM_BINARY_DATA"
	sample_vcf = "##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n1\t123456\trs1\tA\tG\t50\tPASS\t."

	# Simulate pipeline
	s3 = MockS3()
	s3.create_bucket("raw-genomics-bucket")
	s3.put_object("raw-genomics-bucket", "sample.fastq", sample_fastq)
	s3.put_object("raw-genomics-bucket", "sample.bam", sample_bam)
	s3.put_object("raw-genomics-bucket", "sample.vcf", sample_vcf)

	db = MockDynamoDB()
	db.create_table("genomics-metadata")

	lambdas = MockLambda()
	# Validation handler: checks file type and returns status
	def validation_handler(event):
		file = event.get("file")
		if file.endswith(".vcf"):
			return {"status": "VALID", "type": "VCF", "file": file}
		elif file.endswith(".bam"):
			return {"status": "VALID", "type": "BAM", "file": file}
		elif file.endswith(".fastq"):
			return {"status": "VALID", "type": "FASTQ", "file": file}
		else:
			return {"status": "INVALID", "file": file}
	lambdas.create_function("validation-handler", validation_handler)

	# Simulate Step Functions workflow
	sfn = MockStepFunctions()
	sfn.create_state_machine("GenomicsWorkflow", {"States": ["ValidateFile", "ProcessVariants"]})

	# Run sample files through the pipeline
	for fname in ["sample.fastq", "sample.bam", "sample.vcf"]:
		print(f"\n[PIPELINE] Processing {fname}")
		file_data = s3.get_object("raw-genomics-bucket", fname)
		validation_result = lambdas.invoke("validation-handler", {"file": fname})
		print(f"Validation result: {validation_result}")
		if validation_result["status"] == "VALID":
			db.put_item("genomics-metadata", {"sample_id": fname, "type": validation_result["type"], "status": "VALIDATED"})
			sfn_result = sfn.start_execution("GenomicsWorkflow", {"input": fname})
			print(f"Workflow result: {sfn_result}")
		else:
			print(f"File {fname} failed validation.")

	print("\n[MOCK DB] Final genomics-metadata table:")
	print(db.scan("genomics-metadata"))
else:
	from aws_cdk import core as cdk
	from stacks.storage_stack import StorageStack
	from stacks.processing_stack import ProcessingStack
	from stacks.workflow_stack import WorkflowStack

	app = cdk.App()

	# Environment configuration (default to account/region from env)
	env = cdk.Environment(
		account=os.getenv('CDK_DEFAULT_ACCOUNT'),
		region=os.getenv('CDK_DEFAULT_REGION')
	)

	# Tags for cost tracking
	tags = {
		"Project": "GenomicsPrototype",
		"Owner": os.getenv("USER", "unknown"),
		"Environment": os.getenv("ENV", "dev")
	}

	# Storage stack (S3, DynamoDB)
	storage_stack = StorageStack(app, "StorageStack", env=env)
	for k, v in tags.items():
		cdk.Tags.of(storage_stack).add(k, v)

	# Processing stack (Lambda)
	processing_stack = ProcessingStack(app, "ProcessingStack", env=env, storage_stack=storage_stack)
	for k, v in tags.items():
		cdk.Tags.of(processing_stack).add(k, v)

	# Workflow stack (Step Functions)
	workflow_stack = WorkflowStack(app, "WorkflowStack", env=env, storage_stack=storage_stack, processing_stack=processing_stack)
	for k, v in tags.items():
		cdk.Tags.of(workflow_stack).add(k, v)

	app.synth()
