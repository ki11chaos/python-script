# How to use POSCAR_to_xml.py
## Breif description
      First obtain a instance of InputXml, then, creat root, title, structure, ground_state... in order, in case of some
    parameters, which must be gotten from 'pre-input' file, are not exist before use method of InputXml,
    finally, you can get 'input.xml' in your pwd.
## POSCAR
      This file just a normal POSCAR.
## pre-input
* **pre-input to speicify the tag for your own purpose.**
  - *\<pre-input\> format,*
```haskell
    title  = Diamond
    ngridk = 8 8 8
    qpoint = |0.0 0.0 0.0|
    xstype = TDDFT
      ...
```
## k-path
* **When some task related to kpoints, this file should be added.**
  - *\<k-path\> format,*
```haskell
    Gamma = 1.0 0.0 0.0
    K = 0.625 0.375 0.0
    X = 0.5 0.5 0.0 
    L = 0.5 0.0 0.0
      ...
```
## The total mode you can create  
* **Please choose a mode you want to calculate from below:** 
```haskell 
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
## Auto-generate template of pre-files
* **When you choose the first mode '0' above, then more firendly options occur,**
```haskell
    Please choose a number:
        1. <pre-input> for ground state <input.xml>;
        2. <pre-input> for dos <input.xml>;
        3. <pre-input> and <k-path> for band structure <input.xml>;
        4. <pre-input> for rt-TDDFT <input.xml>;
        5. <pre-input> for TDDFT <input.xml>;
        6. <pre-input> for HSE calculation;
        7. <pre-input> for Ion Coordinates Relax;
        8. <pre-input> for SHG (Second Harmonic Generation);
```
**Finally, you edit details carefully, and aslo good luck!**
