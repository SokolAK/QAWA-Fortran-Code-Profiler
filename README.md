# &nbsp; ))) <br/> F\\_/&nbsp; QAWA Fortran Code Profiler

QAWA (Quasi-Aspect-Weaving Approach) FCP is a _Python_-based framework for profiling _Fortran_ source code.<br/>
You can use it to track the control flow and measure the execution time of your procedures.

# Idea
QAWA wraps _Fortran_ subroutines in source files with special code designed to monitor control flow and measure execution time. The following examples illustrate the idea.


* ### Original subroutine:
```
subroutine sssss(x, y, z)
    <<< original code >>>
end subroutine sssss
```

* ### Wrapped subroutine:

```
subroutine sssss(x, y, z)
    <<< qawa profiling code >>>
    call qawa_sssss(x, y, z) 
    <<< qawa profiling code >>>
return
end

subroutine qawa_sssss(x, y, z)
    <<< original code >>>
end subroutine qawa_sssss
```
* ### Original function:
```
function fffff(x, y) result(z)
    <<< original code >>>
return
end
```

* ### Modified function:

```
function fffff(x, y) result(z)
    <<< qawa profiling code >>>
    <<< original code >>>
    <<< qawa profiling code >>>
return
end
```

# Usage
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     )))    QAWA* Fortran  
    F\_/    Code Profiler 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*Quasi-Aspect-Weaving Approach

[QAWA] Help

Usage: qawa <command>

List of commands:
    wrap [out]    --  add profiling wrappers to files listed in qawa.py. 
                      Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.
                      If no [out] is passed, the output filename is set to 'qawa.out'.
    make          --  build wrapped project
    build [out]   --  wrap [out] + make
    unwrap        --  remove profiling wrappers from all files in SOURCE_DIR specified in qawa.py
    restore       --  unwrap + make
    report <out>  --  generate reports based on the given <out> file
    
[QAWA] Done
```

# Example reports
* ### Control flow:
```
QAWA SHORT FLOW REPORT
----------------------
MAIN
[...]
    sapt_driver
        sapt_basinfo
            basinfo
        sapt_interface
            onel_molpro                   |x2
                readoneint_molpro   |x3   |
                square_oneint       |     |
                writeoneint               |
            readocc_molpro         |x2
                read_1rdm_molpro   |
                Diag8              |
                SortOcc            |
                read_nact_molpro   |
            print_occ
            read_mo_molpro   |x2
            prepare_no              |x2
                create_ind          |
                readoneint_molpro   |
                FockGen_mithap      |
                Diag8   |x2         |
            prepare_rdm2_file      |x2
                read_2rdm_molpro   |
                TrRDM2             |
            select_active   |x2
            print_active
            calc_elpot
                get_den   |x2
                get_one_mat   |x2
        sapt_mon_ints      |x2
            get_1el_h_mo   |
        sapt_response
            SaptInter
            read2rdm
            prepare_RDM2val
[...]
```
* ### Execution times:
```
QAWA TIMES REPORT
--------------------------------
* All times expressed in seconds

-------------------
Sums of self times:
-------------------
Wall time: 303.6890
CPU time: 295.1999

-----------------------------------
The most time-consuming procedures:
-----------------------------------
Wall time: sapt_driver [sapt_main.f90]: 303.0693
CPU time: sapt_driver [sapt_main.f90]: 295.1463

------------------------------------------------------
The most time-consuming procedures excluding children:
------------------------------------------------------
Wall time: sapt_ab_ints [sapt_main.f90]:  89.7729
CPU time: sapt_ab_ints [sapt_main.f90]:  89.7401


EXECUTION TIMES sorted by WALL TIME:                                               V DESCENDING V
-------------------------+----------------------+------+--------+----------------+----------------+------------+----------------+----------------+------------
NAME                     | FILE                 | TYPE |  CALLS |       CPU_TIME |      WALL_TIME |        C/W |  SELF_CPU_TIME | SELF_WALL_TIME |   SELF_C/W
-------------------------+----------------------+------+--------+----------------+----------------+------------+----------------+----------------+------------
sapt_driver              | sapt_main.f90        |  S   |      1 |       295.1463 |       303.0693 |       0.97 |         0.0035 |         0.0654 |       0.05
sapt_ab_ints             | sapt_main.f90        |  S   |      1 |        89.7401 |        89.7729 |       1.00 |        89.7401 |        89.7729 |       1.00
e2disp                   | sapt_pol.f90         |  S   |      1 |        76.5387 |        76.6736 |       1.00 |        38.1335 |        38.1591 |       1.00
sapt_response            | sapt_main.f90        |  S   |      2 |        40.9351 |        47.8492 |       0.86 |         0.0024 |         0.0515 |       0.05
calc_resp_casgvb         | sapt_main.f90        |  S   |      2 |        40.9310 |        47.7844 |       0.86 |         0.1511 |         0.1968 |       0.77
e2disp_semi              | sapt_pol.f90         |  S   |      1 |        38.3215 |        38.3961 |       1.00 |        38.2806 |        38.3067 |       1.00
ERPASYMM0                | interpa.f            |  S   |    459 |        30.0698 |        34.9029 |       0.86 |        25.5087 |        28.4627 |       0.90
sapt_interface           | sapt_main.f90        |  S   |      1 |        31.7688 |        32.0481 |       0.99 |        22.3431 |        22.3982 |       1.00
sapt_mon_ints            | sapt_main.f90        |  S   |      2 |        31.1881 |        31.2095 |       1.00 |        31.1842 |        31.2021 |       1.00

[...]
```

# Requirements
* [Python 3.6 (or higher)](https://www.python.org/downloads/)

# Status
_in progress_