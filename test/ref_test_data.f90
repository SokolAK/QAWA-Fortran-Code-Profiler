!start qawa wrapper ##########################################
Subroutine sub1(x, y, z)

use omp_lib
use module
integer :: i 

real :: start, end
real ( kind = 8 ) :: wtime, wtime2
wtime = omp_get_wtime()
call cpu_time(start)

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,I2,A2,I2)')&
'-> test_data.f90 sub1 S',&
OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
close(61)
!$OMP END CRITICAL

call qawa_sub1(x, y, z)

call cpu_time(end)
wtime2 = omp_get_wtime()

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 sub1 S',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL

return
end
!end qawa wrapper ############################################

Subroutine qawa_sub1&
(x, y, z)
    use module
    integer :: i 
    <some code>
End subroutine qawa_sub1

!start qawa wrapper ##########################################
Subroutine sub2 &
(x, y, z)

use omp_lib
use module
real :: r

real :: start, end
real ( kind = 8 ) :: wtime, wtime2
wtime = omp_get_wtime()
call cpu_time(start)

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,I2,A2,I2)')&
'-> test_data.f90 sub2 S',&
OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
close(61)
!$OMP END CRITICAL

call qawa_sub2 &
(x, y, z)

call cpu_time(end)
wtime2 = omp_get_wtime()

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 sub2 S',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL

return
end
!end qawa wrapper ############################################

Subroutine qawa_sub2 &
    (x, y, z)
    use module
    real :: r
    <some code>
End subroutine

!start qawa wrapper ##########################################
subroutine sub3&
(x, y, z)

use omp_lib
real :: r

real :: start, end
real ( kind = 8 ) :: wtime, wtime2
wtime = omp_get_wtime()
call cpu_time(start)

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,I2,A2,I2)')&
'-> test_data.f90 sub3 S',&
OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
close(61)
!$OMP END CRITICAL

call qawa_sub3&
(x, y, z)

call cpu_time(end)
wtime2 = omp_get_wtime()

!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 sub3 S',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL

return
end
!end qawa wrapper ############################################

subroutine qawa_sub3&
    (x, y, z)
    real :: r
    <some code>
end

subroutine not_sub1(x,y)
    <some code>
end


function fun1(x) result(y)
      use omp_lib
integer :: j
real :: y

!start qawa open_qawa_fun1 ##################################
real :: start, end
real ( kind = 8 ) :: wtime, wtime2
wtime = omp_get_wtime()
call cpu_time(start)
!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,I2,A2,I2)')&
'-> test_data.f90 fun1 F',&
OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
close(61)
!$OMP END CRITICAL
!end qawa  ##################################

<some code>

!start qawa close_qawa_fun1 ##################################
call cpu_time(end)
wtime2 = omp_get_wtime()
!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 fun1 F',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL
!end qawa  ##################################

return
end

REAL*8 Function fun2(x)
      use omp_lib
integer :: j

!start qawa open_qawa_fun2 ##################################
real :: start, end
real ( kind = 8 ) :: wtime, wtime2
wtime = omp_get_wtime()
call cpu_time(start)
!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,I2,A2,I2)')&
'-> test_data.f90 fun2 F',&
OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
close(61)
!$OMP END CRITICAL
!end qawa  ##################################

<some code>

!start qawa close_qawa_fun2 ##################################
call cpu_time(end)
wtime2 = omp_get_wtime()
!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 fun2 F',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL
!end qawa  ##################################

Return

!start qawa close_qawa_fun2 ##################################
call cpu_time(end)
wtime2 = omp_get_wtime()
!$OMP CRITICAL
open(61,file=&
'/home/adam.sokol/QCHEM/PROFILING/QAWA&
/outs/&
qawa.out',&
action='write',position='append')
write(61,'(A,2F14.6)')&
'<- test_data.f90 fun2 F',&
end-start, wtime2-wtime
close(61)
!$OMP END CRITICAL
!end qawa  ##################################

End function fun2

function not_fun1(x) result(y)
<some code>
end function