!start qawa wrapper ##########################################
      SUBROUTINE sub1
     $(x, y, z)

      use omp_lib
      use module
      integer :: i 

      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A, A)')
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out'

      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3)')
     $'-> test_data.f 
     $sub1 S',
     $th, ths
      close(q_unit)
      !$OMP END CRITICAL
      call qawa_sub1
     $(x, y, z)

      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_data.f 
     $sub1 S',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
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

      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A, A)')
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out'

      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3)')
     $'-> test_data.f 
     $sub2 S',
     $th, ths
      close(q_unit)
      !$OMP END CRITICAL
      call qawa_sub2
     $(x, y, z)

      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_data.f 
     $sub2 S',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
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
      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A, A)')
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out'

      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3)')
     $'-> test_data.f 
     $fun1 F',
     $th, ths
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>
!start qawa close_qawa_fun1 ##################################
      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_data.f 
     $fun1 F',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      RETURN
      END

      REAL*8 FUNCTION fun2(x)
      use omp_lib
      integer :: j
!start qawa open_qawa_fun2 ##################################
      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A, A)')
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out'

      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3)')
     $'-> test_data.f 
     $fun2 F',
     $th, ths
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>
!start qawa close_qawa_fun2 ##################################
      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_data.f 
     $fun2 F',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      RETURN
!start qawa close_qawa_fun2 ##################################
      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_data.f 
     $fun2 F',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      END FUNCTION fun2

      function not_fun1(x) result(y)
      <some code>
      end function