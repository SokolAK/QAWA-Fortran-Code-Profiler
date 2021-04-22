      Program test
      use omp_lib
      use omp_lib
      use omp_lib
      use omp_lib
C
C
      Implicit Real*8 (A-H,O-Z)
C
      Character*60 Title,FMultTab
C
 !start qawa open_qawa_main ##################################
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
     $action='write')
      write(q_unit,'(A, 2I3)')
     $'-> test_main.f 
     $MAIN M',
     $th, ths
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>

 !start qawa close_qawa_main ##################################
      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write',position='append')
      write(q_unit,'(A, 2I3, 3F14.6)')
     $'<- test_main.f 
     $MAIN M',
     $th, ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL
!end qawa  ##################################

      End