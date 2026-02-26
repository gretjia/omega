import pyarrow.parquet as pq
p=r'D:\Omega_frames\v62_base_l1\host=windows1\20250828_b07c2229.parquet'
pf=pq.ParquetFile(p)
print('rows', pf.metadata.num_rows, 'rgs', pf.metadata.num_row_groups, 'cols', pf.metadata.num_columns)
print('schema:')
for n in pf.schema.names:
    print(n, '::', pf.schema_arrow.field(n).type)
name_to_types={n:set() for n in pf.schema.names}
for i in range(pf.metadata.num_row_groups):
    rg=pf.metadata.row_group(i)
    for j in range(rg.num_columns):
        col=rg.column(j)
        name_to_types[col.path_in_schema].add(str(col.physical_type))
print('drift_cols:')
for n,t in name_to_types.items():
    if len(t)>1:
        print(n, sorted(t))
