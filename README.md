# &nbsp; ))) <br/> F\\_/&nbsp; QAWA Fortran-Code-Profiler
QAWA Fortran-Code-Profiler (or just QAWA) is a Python-based framework for profiling Fortran source code. You can use it to track the control flow, show call chains and measure the execution time of your procedures.<br/>
❗ Note: Profiling of multithreaded programs is currently in an experimental phase.

# 💡 Idea
QAWA wraps Fortran subroutines in source files with special code designed to monitor control flow and measure execution time. The following examples illustrate the idea.

### &nbsp; &nbsp; 💎 Original subroutine:
```
subroutine sssss(x, y, z)
    <<< original code >>>
end subroutine sssss
```
### &nbsp; &nbsp; 🎁 Wrapped subroutine:
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
### &nbsp; &nbsp; 💎 Original function:
```
function fffff(x, y) result(z)
    <<< original code >>>
return
end
```
### &nbsp; &nbsp; 🎁 Modified function:
```
function fffff(x, y) result(z)
    <<< qawa profiling code >>>
    <<< original code >>>
    <<< qawa profiling code >>>
return
end
```

# 📘 Manual
## 🔧 Configuration
Prepare a configuration file based on `QAWA/config_sample.py`.<br/>
You should set the path to your source files and list the procedures you want to profile.
```
# QAWA CONFIGURATION
########################################################################
SOURCE_DIR =        '/home/my_project/source/'
MAIN_FILE =         SOURCE_DIR + 'main.f'
SUBROUTINES_FILES = ['*']
SUBROUTINES =       ['-excluded_subroutine']
FUNCTIONS_FILES =   ['functions.f90']
FUNCTIONS =         ['included_function_1', 'included_function_2']
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

## 🏃 Run
Launch QAWA with the bash script: `./qawa <command>` or the python script: `python qawa.py <command>`.<br/>
Do not pass any `<command>` to display `help`.

```
~~~ ))) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   F\_/  QAWA Fortran-Code-Profiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[QAWA] Help

Usage: run shell script './qawa <command>' or python script 'python qawa.py <command>'

List of commands:
wrap <config.py> -o [out] .... Add profiling wrappers to files listed in <config.py>.
                               Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.
                               If no [out] is passed, the output filename is set to 'qawa.out'.
unwrap <config.py> ........... Restore the original version of the source files listed in <config.py>
                               from before the wrapping process.
report <out> ................. Generate reports based on the given <out> file.
```

## ♻️ Typical workflow
### &nbsp; &nbsp; 📈 Wrapping and profiling your project:
```
qawa wrap (1) ->
-> check wrap report (2) ->
-> rebuild your project ->
-> run the executable ->
-> qawa report (3)
```
1. Before wrapping QAWA automatically creates a copy of your source files (backup files have the `.qawa_copy` extension).
2. Wrap report is saved in the `QAWA/outs/qawa_wrap_report` file. It shows which procedures have been actually wrapped. This step is optional.
3. Run `qawa report` after the executable has finished running.

### &nbsp; &nbsp; 🔙 Removing QAWA from your project:
```
qawa unwrap (1) -> rebuild your project
```
1. `unwrap` restore the original version of your source from `.qawa_copy` files

## 📋 Reports
The `report <out>` command generate the following text formatted reports based on the `<out>` file:
- control flow report: `<out>.flow`
- short control flow report with rolled loops: `<out>.flow_short`
- bunch of call chains reports with execution times: `<out>.chains[...]`

### &nbsp;&nbsp; 📄 Examples
##### &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 🌊`<out>.short_flow`:
```
QAWA FLOW REPORT (Rollup: True)
File: outs/qawa_c1.out.flow_short
Date: 22.04.2021 01:02:21
-------------------------------

#1 MAIN

[...]

#1 .   sapt_driver
#1 .   .   sapt_basinfo
#1 .   .   .   basinfo
#1 .   .   sapt_interface
#1 .   .   .   onel_molpro                   |x2
#1 .   .   .   .   readoneint_molpro   |x3   |
#1 .   .   .   .   square_oneint       |     |
#1 .   .   .   .   writeoneint               |
#1 .   .   .   readocc_molpro         |x2
#1 .   .   .   .   read_1rdm_molpro   |
#1 .   .   .   .   Diag8              |
#1 .   .   .   .   SortOcc            |
#1 .   .   .   .   read_nact_molpro   |
#1 .   .   .   print_occ
#1 .   .   .   read_mo_molpro   |x2
#1 .   .   .   readtwoint
#1 .   .   .   .   open_Sorter
#1 .   .   .   .   dump_Sorter

[...]
```

##### &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 🌊`<out>.short_flow` #2:
```
QAWA FLOW REPORT (Rollup: True)
File: outs/qawa_dynamic.out.flow_short
Date: 22.04.2021 00:10:01
-------------------------------

#1 MAIN
#1 .   wakeup
#1 .   .   work
#1 .   greeting
#1 .   .   prepare_hello
#1 .   .   .   work
PARALLEL 3 =======================================================================================================================
#1 .   .   execute_hello   |x8                    #2 .   .   execute_hello   |x5                    #3 .   .   execute_hello   |x3
#1 .   .   .   say_hello   |                      #2 .   .   .   say_hello   |                      #3 .   .   .   say_hello   |   
#1 .   .   .   .   work    |                      #2 .   .   .   .   work    |                      #3 .   .   .   .   work    |   
SEQUENTIAL -----------------------------------------------------------------------------------------------------------------------
#1 .   .   finish_hello
#1 .   .   .   work
#1 .   .   work
#1 .   .   prepare_hello
#1 .   .   .   work
PARALLEL 3 =======================================================================================================================
#1 .   .   execute_hello   |x9                    #2 .   .   execute_hello   |x4                    #3 .   .   execute_hello   |x3
#1 .   .   .   say_hello   |                      #2 .   .   .   say_hello   |                      #3 .   .   .   say_hello   |  
#1 .   .   .   .   work    |                      #2 .   .   .   .   work    |                      #3 .   .   .   .   work    |  
SEQUENTIAL -----------------------------------------------------------------------------------------------------------------------
#1 .   .   finish_hello
#1 .   .   .   work
#1 .   .   work
#1 .   bye
```

##### &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ⛓️ `<out>.chains`:
```
QAWA CHAINS REPORT (Rollup: False, Reverse: False, Sort key: self_wtime)
File: outs/qawa_c8.out.chains-self_wtime
Date: 22.04.2021 01:04:49
------------------------------------------------------------------------
* W-TIME = wall time, C-TIME = CPU time
* All times expressed in seconds
------------------------------------------------------------------------

     W-TIME |      C-TIME |    C/W | SELF W-TIME | SELF C-TIME |    C/W | CALLS | THREADS | CHAIN
------------+-------------+--------+-------------+-------------+--------+-------+---------+---------------------------------------------------------------------------------------------------------------------------------
    56.7938 |    454.2902 |   8.00 |     56.7938 |    454.2902 |   8.00 |    11 |     1/1 | MAIN -> sapt_driver -> sapt_ab_ints -> tran4_gen
    38.1309 |     39.3263 |   1.03 |     38.0859 |     39.0671 |   1.03 |     1 |     1/1 | MAIN -> sapt_driver -> e2disp -> e2disp_semi
    76.1829 |     79.3851 |   1.04 |     37.9631 |     39.3624 |   1.04 |     1 |     1/1 | MAIN -> sapt_driver -> e2disp
    25.1468 |     38.5890 |   1.53 |     24.1361 |     30.8087 |   1.28 |     2 |     1/1 | MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> ERPASYMMXY -> ERPASYMM0
    21.7006 |     22.9174 |   1.06 |     20.9240 |     21.8996 |   1.05 |     1 |     1/1 | MAIN -> sapt_driver -> sapt_interface -> readtwoint
    19.6822 |    157.4464 |   8.00 |     19.6822 |    157.4464 |   8.00 |     4 |     1/1 | MAIN -> sapt_driver -> sapt_mon_ints -> tran4_gen
     8.6152 |      8.6125 |   1.00 |      8.6152 |      8.6125 |   1.00 |     2 |     1/1 | MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> ACEneERPA_FOFO
     6.4933 |     51.8933 |   7.99 |      6.4894 |     51.8656 |   7.99 |     2 |     1/1 | MAIN -> sapt_driver -> sapt_interface -> prepare_no -> FockGen_mithap
     5.8853 |     47.0801 |   8.00 |      5.8853 |     47.0801 |   8.00 |     2 |     1/1 | MAIN -> sapt_driver -> e1exchs2 -> tran4_gen
     3.0947 |     24.7562 |   8.00 |      3.0947 |     24.7562 |   8.00 |     1 |     1/1 | MAIN -> sapt_driver -> e1exchs2 -> make_K
     2.9415 |     23.5293 |   8.00 |      2.9415 |     23.5293 |   8.00 |     1 |     1/1 | MAIN -> sapt_driver -> sapt_interface -> calc_elpot -> make_J2
     2.8728 |     22.9807 |   8.00 |      2.8728 |     22.9807 |   8.00 |     1 |     1/1 | MAIN -> sapt_driver -> e1elst -> make_J1
     2.6433 |      5.4145 |   2.05 |      2.6433 |      5.4145 |   2.05 |     2 |     1/1 | MAIN -> sapt_driver -> e2exdisp -> inter_A2_XX
     2.3128 |      7.8600 |   3.40 |      2.3128 |      7.8600 |   3.40 |     2 |     1/1 | MAIN -> sapt_driver -> e2exdisp -> inter_A2_YX
     3.3094 |      0.4823 |   0.15 |      1.8927 |      0.2740 |   0.14 |   457 |     1/1 | MAIN -> sapt_driver -> sapt_response -> calc_resp_casgvb -> Y01CAS_FOFO -> pack_Eblock -> ERPASYMM0

[...]
```

##### &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ⛓️ `<out>.chains` #2:
```
QAWA CHAINS REPORT (Rollup: False, Reverse: True, Sort key: wtime)
File: outs/qawa_dynamic.out.chains-wtime-rev
Date: 22.04.2021 00:10:01
------------------------------------------------------------------
* W-TIME = wall time, C-TIME = CPU time
* All times expressed in seconds
------------------------------------------------------------------

     W-TIME |      C-TIME |    C/W | SELF W-TIME | SELF C-TIME |    C/W | CALLS | THREADS | PROCEDURE       | CALLING CHAIN
------------+-------------+--------+-------------+-------------+--------+-------+---------+-----------------+-----------------------------------------
    86.8327 |    299.6527 |   3.45 |      0.0010 |      0.0010 |   1.00 |     1 |     1/1 | MAIN            |
    84.6309 |    297.4511 |   3.51 |      0.0036 |      1.4138 | 393.05 |     1 |     1/1 | greeting        | <- MAIN
    60.2304 |     60.2304 |   1.00 |      0.0018 |      0.0019 |   1.05 |     4 |     5/5 | execute_hello   | <- greeting <- MAIN
    60.2286 |     60.2285 |   1.00 |      0.0017 |      0.0015 |   0.86 |     4 |     5/5 | say_hello       | <- execute_hello <- greeting <- MAIN
    60.2269 |     60.2270 |   1.00 |     60.2269 |     60.2270 |   1.00 |     4 |     5/5 | work            | <- say_hello <- execute_hello <- greeting <- MAIN
    54.8955 |     54.8955 |   1.00 |      0.0013 |      0.0013 |   1.02 |     9 |     2/5 | execute_hello   | <- greeting <- MAIN
    54.8942 |     54.8942 |   1.00 |      0.0029 |      0.0028 |   0.96 |     9 |     2/5 | say_hello       | <- execute_hello <- greeting <- MAIN
    54.8913 |     54.8914 |   1.00 |     54.8913 |     54.8914 |   1.00 |     9 |     2/5 | work            | <- say_hello <- execute_hello <- greeting <- MAIN
    54.8446 |     54.8446 |   1.00 |      0.0018 |      0.0017 |   0.95 |     6 |     3/5 | execute_hello   | <- greeting <- MAIN
    54.8428 |     54.8429 |   1.00 |      0.0023 |      0.0024 |   1.07 |     6 |     3/5 | say_hello       | <- execute_hello <- greeting <- MAIN
    54.8406 |     54.8405 |   1.00 |     54.8406 |     54.8405 |   1.00 |     6 |     3/5 | work            | <- say_hello <- execute_hello <- greeting <- MAIN
    51.8680 |     51.8677 |   1.00 |      0.0019 |      0.0015 |   0.79 |    17 |     1/5 | execute_hello   | <- greeting <- MAIN
    51.8662 |     51.8662 |   1.00 |      0.0040 |      0.0043 |   1.09 |    17 |     1/5 | say_hello       | <- execute_hello <- greeting <- MAIN
    51.8622 |     51.8619 |   1.00 |     51.8622 |     51.8619 |   1.00 |    17 |     1/5 | work            | <- say_hello <- execute_hello <- greeting <- MAIN
    49.2113 |     49.2112 |   1.00 |      0.0014 |      0.0012 |   0.86 |     4 |     4/5 | execute_hello   | <- greeting <- MAIN
    49.2099 |     49.2100 |   1.00 |      0.0019 |      0.0019 |   1.02 |     4 |     4/5 | say_hello       | <- execute_hello <- greeting <- MAIN
    49.2081 |     49.2081 |   1.00 |     49.2081 |     49.2081 |   1.00 |     4 |     4/5 | work            | <- say_hello <- execute_hello <- greeting <- MAIN
    15.0279 |     15.0272 |   1.00 |     15.0279 |     15.0272 |   1.00 |     2 |     1/1 | work            | <- greeting <- MAIN
     4.8711 |      4.8708 |   1.00 |      0.0003 |      0.0003 |   1.07 |     2 |     1/1 | prepare_hello   | <- greeting <- MAIN
     4.8707 |      4.8705 |   1.00 |      4.8707 |      4.8705 |   1.00 |     2 |     1/1 | work            | <- prepare_hello <- greeting <- MAIN
     4.4980 |      5.0899 |   1.13 |      0.0008 |      0.0016 |   2.09 |     2 |     1/1 | finish_hello    | <- greeting <- MAIN
     4.4972 |      5.0883 |   1.13 |      4.4972 |      5.0883 |   1.13 |     2 |     1/1 | work            | <- finish_hello <- greeting <- MAIN
     2.2008 |      2.2006 |   1.00 |      0.0007 |      0.0007 |   1.00 |     1 |     1/1 | wakeup          | <- MAIN
     2.2001 |      2.2000 |   1.00 |      2.2001 |      2.2000 |   1.00 |     1 |     1/1 | work            | <- wakeup <- MAIN
     0.0001 |      0.0001 |   1.00 |      0.0001 |      0.0001 |   1.00 |     1 |     1/1 | bye             | <- MAIN
```

## 📜 Requirements
&nbsp; &nbsp; &nbsp; &nbsp; 🐍 [Python 3.6 (or higher)](https://www.python.org/downloads/)

## 🚦 Status
* implementing support for multithreaded applications
* testing