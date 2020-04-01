# forms organization

```
├── Delanteros
     ├─  minion-minion.form
     ├─  minion-self.form
     ├─  minion-manager.form
     ├─  manager-minion.form
     └─  manager-self.form
├── Centrales
     ├─  minion-minion.form
     ├─  minion-self.form
     ├─  minion-manager.form
     ├─  manager-minion.form
     └─  manager-self.form
├── Defensas
     ├─  minion-minion.form
     ├─  minion-self.form
     ├─  minion-manager.form
     ├─  manager-minion.form
     └─  manager-self.form
└─ Porteros
     ├─  minion-minion.form
     ├─  minion-self.form
     ├─  minion-manager.form
     ├─  manager-minion.form
     └─  manager-self.form
```

From the assigments-step we obtained the following:

centro_1 will review:

- centro_1 **self evaluation**
- Modric **Manager evaluation**
- centro_2: peer evaluation
- centro_3: peer evaluation
- delantero_1: peer evaluation
- delantero_3: peer evaluation

Let's focus in centro_1, he will receive the following forms:

 - centro_1: centrales/minion-self.form
 - Modric: centrales/minion-manager.form
 - centro_2: centrales/minion-minion.form
 - centro_3: centrales/minion-minion.form
 - delantero_1: delanteros/minion-minion.form
 - delantero_3: delanteros/minion-minion.form

This revision will append these rows in the following files:

_Example_ "centrales/minion-self.answers":

|   I am   | question one | question two | question three |
| :------- | :----------- | :----------- | :------------- |
| ...      | ...          | ...          | ...            |
| centro_1 | answer one   | answer two   | answer three   |

_Example_ "centrales/minion-manager.answers":

|   I am   | reviewing | question one | question two | question three |
| :------- | :-------- | :----------- | :----------- | :------------- |
| centro_1 | Modric    | answer one   | answer two   | answer three   |

_Example_ "centrales/minion-minion.answers":

|   I am   | reviewing | question one | question two | question three |
| :------- | :-------- | :----------- | :----------- | :------------- |
| centro_1 | centro_2  | answer one   | answer two   | answer three   |
| centro_1 | centro_3  | answer one   | answer two   | answer three   |

_Example_ "delanteros/minion-minion.answers":

|   I am   |  reviewing  | question one | question two | question three |
| :------- | :---------- | :----------- | :----------- | :------------- |
| centro_1 | delantero_1 | answer one   | answer two   | answer three   |
| centro_1 | delantero_3 | answer one   | answer two   | answer three   |
