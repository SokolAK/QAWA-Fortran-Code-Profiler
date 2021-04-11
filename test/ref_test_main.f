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
      real :: start, end
      real ( kind = 8 ) :: wtime, wtime2
      wtime = omp_get_wtime()
      call cpu_time(start)

      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write')
      write(61,'(A,I2,A2,I2)') '-> test_main.f MAIN M',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
      !end qawa  ##################################

      <some code>

 
      !start qawa  ##################################
      call cpu_time(end)
      wtime2 = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'/home/adam.sokol/QCHEM/PROFILING/QAWA
     $/outs/
     $qawa.out',
     $action='write',position='append')
      write(61,'(A,2F14.6)') '<- test_main.f MAIN M',
     $end-start, wtime2-wtime
      close(61)
      !$OMP END CRITICAL
      !end qawa  ##################################

      End