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
      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)

      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write')
      write(61,'(A,I2,I2)') '-> 
     $test_main.f 
     $MAIN M',
     $OMP_GET_THREAD_NUM()+1, OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
      !end qawa  ##################################

      <some code>

 
      !start qawa  ##################################
      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)') '<- 
     $test_main.f 
     $MAIN M',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL
      !end qawa  ##################################

      End