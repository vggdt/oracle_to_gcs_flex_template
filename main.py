import json
import decimal
import datetime
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.jdbc import ReadFromJdbc


class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument('--connection_url', required=True)
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--query', required=True)
        parser.add_argument('--output_path', required=True)


class RowToJsonDictFn(beam.DoFn):
    def process(self, row):
        d = {}
        for k, v in row._asdict().items():
            if isinstance(v, decimal.Decimal):
                d[k] = float(v)
            elif isinstance(v, datetime.datetime):
                d[k] = v.isoformat()
            elif v is None:
                d[k] = None
            else:
                d[k] = v
        yield d


class WriteJsonFileFn(beam.DoFn):
    def __init__(self, output_prefix):
        self.output_prefix = output_prefix
        self.shard_index = 0

    def process(self, batch):
        filename = f"{self.output_prefix}_part{self.shard_index}.json"
        self.shard_index += 1

        with beam.io.filesystems.FileSystems.create(filename) as f:
            content = json.dumps(batch, ensure_ascii=False)
            f.write(content.encode('utf-8'))

        yield filename


def run():
    pipeline_options = PipelineOptions()
    opts = pipeline_options.view_as(CustomOptions)

    # Gera timestamp UTC-3
    timestamp_str = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).strftime('%Y%m%d_%H%M%S')
    output_prefix = f"{opts.output_path}/data_{timestamp_str}"

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "Read from Oracle" >> ReadFromJdbc(
                table_name="",  # Required , but using query.
                driver_class_name= 'oracle.jdbc.driver.OracleDriver',
                jdbc_url=opts.connection_url,
                username=opts.username,
                password=opts.password,
                query=opts.query,
            )
            | "Row → dict safely" >> beam.ParDo(RowToJsonDictFn())
            | "Batch JSON arrays" >> beam.BatchElements(min_batch_size=20, max_batch_size=1000)
            | "Write JSON to GCS" >> beam.ParDo(WriteJsonFileFn(output_prefix))
        )


if __name__ == "__main__":
    run()
