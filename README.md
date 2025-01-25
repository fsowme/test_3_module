# test_3_module

| Эксперимент | batch.size | linger.ms | compression.type | buffer.memory | batch.max.rows | Source Record Write Rate (кops/sec) |
|------------:|-----------:|----------:|-----------------:|--------------:|---------------:|------------------------------------:|
|           1 |        500 |      1000 |                - |      33554432 |            100 |                                   5 |
|           2 |     526000 |       100 |           snappy |     134217728 |           1000 |                                 162 |
