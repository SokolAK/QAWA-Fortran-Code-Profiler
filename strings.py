def get_banner():
	return f"""~~~ ))) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   F\_/  QAWA Fortran-Code-Profiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

def get_wrapper_header():
	return '!start qawa wrapper ##########################################'

def get_wrapper_footer():
	return '!end qawa wrapper ############################################'

def get_fragment_header(str=''):
	return f'!start qawa {str} ##################################'

def get_fragment_footer(str=''):
	return f'!end qawa {str} ##################################'

def get_prefix():
	return 'qawa_'


def get_wrapper_declarations(script_dir, out_file):
    return f"""      integer :: q_sys_start, q_sys_end
      real(kind=8) :: q_wtime_start, q_wtime_end, q_cpu_start, q_cpu_end
      character(len=256) :: q_file, th
      integer :: ths, parent_th
      real(kind=8) :: cpu_rate
      integer :: count_rate,count_max
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      parent_th = omp_get_ancestor_thread_num(omp_get_level()-1)+1
      ths = OMP_GET_NUM_THREADS()

      write (th, '(I0, A, I0)') parent_th,'-',OMP_GET_THREAD_NUM()+1

      write (q_file, '(A, A)')
     $'{script_dir}
     $/outs/
     ${out_file}'
"""

def get_wrapper_time_start(file, name, typ, file_mode=",position='append'"):
    return f"""      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(10,file=
     $q_file,
     $action='write'{file_mode})
      write(10,'(A, A, A8, A, I3)')
     $'-> {file} 
     ${name} {typ}',
     $' ', th, ' ', ths
      close(10)
      !$OMP END CRITICAL"""

def get_wrapper_time_end(file, name, typ, file_mode=",position='append'"):
    return f"""      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(10,file=
     $q_file,
     $action='write'{file_mode})
      write(10,'(A, A, A8, A, I3, 3F14.6)')
     $'<- {file} 
     ${name} {typ}',
     $' ', th, ' ', ths,
     $(q_sys_end-q_sys_start)/cpu_rate, q_cpu_end-q_cpu_start, 
     $q_wtime_end-q_wtime_start
      close(10)
      !$OMP END CRITICAL"""

