!start qawa wrapper ##########################################
      SUBROUTINE sub1
     $(x, y, z)

      use omp_lib
      use module
      integer :: i 

      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)

      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,I2,I2)')
     $'-> test_data.f 
     $sub1 S',
     $OMP_GET_THREAD_NUM()+1, OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL

      call qawa_sub1
     $(x, y, z)

      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- test_data.f 
     $sub1 S',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL

      return
      end
!end qawa wrapper ############################################

      SUBROUTINE qawa_sub1
     $(x, y, z)
      use module
      integer :: i 
      <some code>
      END

!start qawa wrapper ##########################################
      SUBROUTINE sub2
     $(x, y, z)

      use omp_lib
      integer :: i 

      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)

      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,I2,I2)')
     $'-> test_data.f 
     $sub2 S',
     $OMP_GET_THREAD_NUM()+1, OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL

      call qawa_sub2
     $(x, y, z)

      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- test_data.f 
     $sub2 S',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL

      return
      end
!end qawa wrapper ############################################

      SUBROUTINE qawa_sub2
     $(x, y, z)
C comment
      integer :: i 
      <some code>
      END SUBROUTINE
      
      subroutine not_sub1(x,y)
      <some code>
      end

      
      FUNCTION fun1(x) result(y)
      use omp_lib
      integer :: j
      real :: y

!start qawa open_qawa_fun1 ##################################
      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,I2,I2)')
     $'-> test_data.f 
     $fun1 F',
     $OMP_GET_THREAD_NUM()+1, OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>

!start qawa close_qawa_fun1 ##################################
      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- test_data.f 
     $fun1 F',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL
!end qawa  ##################################

      RETURN
      END

      REAL*8 FUNCTION fun2(x)
      use omp_lib
      integer :: j

!start qawa open_qawa_fun2 ##################################
      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,I2,I2)')
     $'-> test_data.f 
     $fun2 F',
     $OMP_GET_THREAD_NUM()+1, OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>

!start qawa close_qawa_fun2 ##################################
      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- test_data.f 
     $fun2 F',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL
!end qawa  ##################################

      RETURN

!start qawa close_qawa_fun2 ##################################
      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- test_data.f 
     $fun2 F',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL
!end qawa  ##################################

      END FUNCTION fun2

      function not_fun1(x) result(y)
      <some code>
      end function