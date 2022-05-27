# How to use POSCAR_to_xml.py
## Breif description
      First obtain a instance of InputXml, then, creat root, title, structure, ground_state... in order, in case of some
    parameters, which must be gotten from 'pre-input' file, are not exist before use method of InputXml,
    finally, you can get 'input.xml' in your pwd.
## POSCAR
## input
## The total mode you can create
```
        Please choose a mode you want to calculate from below:
        0. generate template of <pre-input>, <k-path> or ...;
        1. generate ground state <input.xml>;
        2. generate dos <input.xml>;
        3. generate band structure <input.xml>;
        4. generate rt-TDDFT based on the ground state <input.xml>;
        5. generate TDDFT based on the ground state <input.xml>;
        6. generate HSE calculation <input.xml>;
        7. generate Ion Coordinates Relax <input.xml>;
        8. generate SHG (Second Harmonic Generation) <input.xml>;
```
