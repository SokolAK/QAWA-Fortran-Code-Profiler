# &nbsp; ))) <br/> F\\_/&nbsp; QAWA Fortran Code Profiler

QAWA (Quasi-Aspect-Weaving Approach) FCP is a _Python_-based framework for profiling _Fortran_ source code.<br/>
You can use it to track the control flow and measure the execution time of your procedures.

# Idea
QAWA wraps _Fortran_ subroutines in source files with special code designed to monitor control flow and measure execution time.<br/>
The following examples illustrate the idea.


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

# Requirements
* Python 3.6 or higher

# Status
_in progress_