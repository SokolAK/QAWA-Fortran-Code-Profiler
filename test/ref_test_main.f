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
 !start qawa  ##################################
      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      character(len=256) :: q_file
      integer :: th, ths
      real(kind=8) :: cpu_rate
      integer :: count_rate,count_max
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
      open(10,file=
     $q_file,
     $action='write')
      write(10,'(A, 2I3)')
     $'-> test_main.f 
     $MAIN M',
     $th, ths
      close(10)
      !$OMP END CRITICAL
!end qawa  ##################################

      <some code>

      End