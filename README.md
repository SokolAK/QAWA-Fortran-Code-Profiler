# &nbsp; ))) <br/> F\\_/&nbsp; QAWA Fortran-Code-Profiler

QAWA Fortran-Code-Profiler is a Python-based framework for profiling Fortran source code. You can use it to track the control flow, show call chains and measure the execution time of your procedures.

# :bulb: Idea
QAWA wraps Fortran subroutines in source files with special code designed to monitor control flow and measure execution time. The following examples illustrate the idea.

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

# :blue_book: Manual

## :wrench: Configuration
Set the path to your source files and list the procedures you want to profile in the `QAWA/config.py`:
```
# QAWA CONFIGURATION
########################################################################
SOURCE_DIR =        '/home/my_project/source/'
MAIN_FILE =         SOURCE_DIR + 'main.f'
SUBROUTINES_FILES = ['*']
SUBROUTINES =       ['-excluded_subroutine']
FUNCTIONS_FILES =   ['functions.f90']
SUBROUTINES_FILES = ['included_function_1', 'included_function_2']
########################################################################
#
# HELP
#
# SOURCE_DIR        -- path to your source files
# MAIN_FILE         -- path to your main file
# SUBROUTINES_FILES -- list of files with subroutines to wrap
# SUBROUTINES       -- list of subroutines to wrap
# FUNCTIONS_FILES   -- list of files with functions to wrap
# FUNCTIONS         -- list of functions to wrap
#
# You can use the following notation in SUBROUTINES_FILES, SUBROUTINES,
# FUNCTIONS_FILES and FUNCTIONS:
# 'name'  -- adds file/procedure 'name' to the wrapping list
# '-name' -- excludes file/procedure 'name' from the wrapping list
# '*'     -- adds all files from SOURCE_DIR or procedures from
#            SUBROUTINES_FILES/FUNCTIONS_FILES to the wrapping list
```

## :arrow_forward: Usage
Run QAWA with the bash script: `./qawa <command>` or the python script: `python qawa.py <command>`.<br/>
Run without a `<command>` to open `help`.

```
~~~ ))) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   F\_/  QAWA Fortran-Code-Profiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[QAWA] Help

Usage: run shell script './qawa <command>' or python script 'python qawa.py <command>'

List of commands:
wrap [out] ...... add profiling wrappers to files listed in config.py.
                  Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.
                  If no [out] is passed, the output filename is set to 'qawa.out'.
unwrap .......... restore the original version of the source files from before the wrapping process
report <out> .... generate reports based on the given <out> file
```

## :recycle: Typical workflow
### :chart_with_upwards_trend: Wrapping and profiling your project
```
qawa wrap (1) ->
-> check wrap report (2) ->
-> rebuild your project ->
-> run the executable ->
-> qawa report (3)
```
(1) before wrapping QAWA automatically creates a copy of your source files<br/>
&nbsp;&nbsp;&nbsp;&nbsp; (backup files have the `.qawa_copy` extension).<br/>
(2) wrap report is saved in the `QAWA/outs/qawa_wrap_report` file.<br/>
&nbsp;&nbsp;&nbsp;&nbsp; It shows which procedures have been actually wrapped. This step is optional<br/>
(3) after the executable has finished running

### :back: Removing QAWA from your project
```
qawa unwrap (1) -> rebuild your project
```
(1) `unwrap` restore the original version of your source from `.qawa_copy` files

## :page_facing_up: Reports
The `report <out>` command generate the following text formatted reports based on the `<out>` file:
- control flow report: `<out>.flow`
- short control flow report with rolled loops: `<out>.short_flow`
- procedures execution times report: `<out>.times`
- call chains report with execution times: `<out>.chains`

### Examples
* #### `<out>.short_flow`:
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
* #### `<out>.times`:
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

* #### `<out>.chains`:
```
QAWA CHAINS REPORT
--------------------------------------------------------------
* W-TIME = wall time, C-TIME = CPU time, C/W = C-TIME / W-TIME
* All times expressed in seconds

V  DESC.  V
SELF W-TIME  SELF C-TIME     C/W   COUNT  CHAIN
---------------------------------------------------------------------------------------------------------------------------------------------
    89.6058      89.5601    1.00      11  MAIN -> sapt_driver -> sapt_ab_ints -> tran4_gen
    38.2410      38.2208    1.00       1  MAIN -> sapt_driver -> e2disp -> e2disp_semi
    38.1789      38.1563    1.00       1  MAIN -> sapt_driver -> e2disp
    30.1765      30.1547    1.00       4  MAIN -> sapt_driver -> sapt_mon_ints -> tran4_gen
    25.1398      25.1229    1.00       2  MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> ERPASYMMXY -> ERPASYMM0
    21.6229      21.4486    0.99       1  MAIN -> sapt_driver -> sapt_interface -> readtwoint
     8.7008       8.6928    1.00       2  MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> ACEneERPA_FOFO
     5.0880       5.0701    1.00       2  MAIN -> sapt_driver -> sapt_interface -> prepare_no -> FockGen_mithap
     4.5050       4.5018    1.00       2  MAIN -> sapt_driver -> e1exchs2 -> tran4_gen
     4.3428       4.3355    1.00       4  MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> ERPASYMMXY -> ERPASYMM0 -> Diag8
     3.1237       0.3108    0.10     457  MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> Y01CAS_FOFO -> pack_Eblock -> ERPASYMM0
     3.0766       3.0754    1.00       1  MAIN -> sapt_driver -> sapt_interface -> calc_elpot -> make_J2
     2.8640       2.7931    0.98       1  MAIN -> sapt_driver -> e2exdisp

[...]
```


# Requirements
* [Python 3.6 (or higher)](https://www.python.org/downloads/)

# Status
_in progress_