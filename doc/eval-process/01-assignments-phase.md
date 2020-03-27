# Assignment phase

### ⤵️ Input:

1. **org chart**: for each employee we'll need her/his area, lead and team

_Example_ 📙: org chart represented as a .csv

```
Zidane  ; players ; Floren ; CPM         ;
Benzema ; players ; Zidane ; strikers    ;
Modric  ; players ; Zidane ; midfielders ;
Ramos   ; players ; Zidane ; defenders   ;
```

### Output ➡️:

1. Relations `reviewee - (reviewers, reviewType)[]`

_Example_ 📙

```yaml
midfiel_1:
  - midfiel_1: SELF
  - midfiel_2: PEER
  - midfiel_3: PEER
  - Modric: MANAGER
  - striker_1: PEER
  - striker_3: PEER
midfield_2:
  - ...
```

***

## Subphases

- Managers choose assignments
- Volunteer assignments requests ***not defined***
- Assignments verification

From the plain org chart we can create the org tree.

_Example_ 📙parsed info from the .csv:

```
Floren                        (CPMs)
├── Valdano                   (CPMs)
     ├─  suit_1               (suits)
     └─  suit_2               (suits)
└── Zidane                    (CPMs)
     ├─  Benzema              (strikers)
           ├── striker_1      (strikers)
           ├── striker_2      (strikers)
           └─  striker_3      (strikers)
     ├─  Modric               (midfielders)
           ├── midfiel_1      (midfielders)
           ├── midfiel_2      (midfielders)
           ├── midfiel_3      (midfielders)
           └─  midfiel_4      (midfielders)
     ├─  Ramos                (defenders)
           ├── defender_1     (defenders)
           ├── defender_2     (defenders)
           ├── defender_3     (defenders)
           └─  defender_4     (defenders)
     └─  Casillas             (goalkeepers)
           ├── goalkeeper_1   (goalkeepers)
           └─  goalkeeper_2   (goalkeepers)
```

both Zidane, Benzema, Modric, Ramos, Casillas, and Valdano receives one **`Assigments Form`** each, since they all are leads.

_Example_ 📙
Assigment form recieved and filled by Modric (as lead of the midfields team)

```
Q1. In each row, you will find one of your minions. Each row means who will evaluate that minion.
(It is no necessary to mark their self-evaluation since that will be automated).

| she/he will evaluate:  | midfiel_1 | midfiel_2 | midfiel_3 | midfiel_4 |
| ---------------------- | :-------: | :-------: | :-------: | :-------: |
| midfiel_1              |           |    YES    |    YES    |           |
| midfiel_2              |    YES    |           |           |           |
| midfiel_3              |           |    YES    |           |    YES    |
| midfiel_4              |    YES    |           |    YES    |           |

Q2. Will midfiel_1 review anyone else in the company (comma separated)?
striker_1,striker_3

Q3. Will midfiel_2 review anyone else in the company (comma separated)?

Q4. Will midfiel_3 review anyone else in the company (comma separated)?

Q5. Will midfiel_4 review anyone else in the company (comma separated)?
defender_3
```

This means that Modric, as lead of a team, has decided the following assigments:

midfiel_1 will review:

- midfiel_1: self evaluation
- Modric: Manager evaluation
- midfiel_2: peer evaluation
- midfiel_3: peer evaluation
- striker_1: peer evaluation
- striker_3: peer evaluation

...

midfiel_4 will review:

- midfiel_4 self evaluation
- Modric: Manager evaluation
- midfiel_1: peer evaluation
- midfiel_3: peer evaluation
- defender_3: peer evaluation

...

We need to
