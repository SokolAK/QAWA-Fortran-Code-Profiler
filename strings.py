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
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A)')
     $'{script_dir}
     $/outs/
     ${out_file}'
"""

def get_wrapper_time_start(filename, name, typ, file_mode=",position='append'"):
    return f"""      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write'{file_mode})
      write(q_unit,'(A, 2I3, 3F24.6)')
     $'-> {filename} 
     ${name} {typ}',
     $th, ths,
     $q_sys_start/cpu_rate, q_cpu_start, q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL"""

def get_wrapper_time_end(filename, name, typ, file_mode=",position='append'"):
    return f"""      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)
      
      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write'{file_mode})
      write(q_unit,'(A, 2I3, 3F24.6)')
     $'<- {filename} 
     ${name} {typ}',
     $th, ths,
     $q_sys_end/cpu_rate, q_cpu_end, q_wtime_end
      close(q_unit)
      !$OMP END CRITICAL"""


def get_qawa_start_procedure(script_dir, out_file, file_mode=",position='append'"):
    return f"""
      subroutine qawa_S(filename, name, typ)
      use omp_lib
      character(*) :: filename, name, typ

      integer :: q_sys_start
      real(kind=8) :: q_wtime_start, q_cpu_start
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A)')
     $'{script_dir}
     $/outs/
     ${out_file}'

      q_wtime_start = omp_get_wtime()
      call cpu_time(q_cpu_start)
      call SYSTEM_CLOCK(q_sys_start)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write'{file_mode})
      write(q_unit,'(6A, 2I3, 3F24.3)')
     $'-> ', filename, ' ', name, ' ', typ, 
     $th, ths,
     $q_sys_start/cpu_rate, q_cpu_start, q_wtime_start
      close(q_unit)
      !$OMP END CRITICAL
      end subroutine qawa_S

"""

def get_qawa_end_procedure(script_dir, out_file, file_mode=",position='append'"):
    return f"""
      subroutine qawa_E(filename, name, typ)
      use omp_lib
      character(*) :: filename, name, typ

      integer :: q_sys_end
      real(kind=8) :: q_wtime_end, q_cpu_end
      real(kind=8) :: cpu_rate
      character(len=256) :: q_file
      integer :: th, ths, count_rate, count_max, q_unit
      call system_clock(count_rate=count_rate)
      call system_clock(count_max=count_max)
      cpu_rate = real(count_rate)
      th = OMP_GET_THREAD_NUM() + 1
      ths = OMP_GET_NUM_THREADS()

      write (q_file, '(A)')
     $'{script_dir}
     $/outs/
     ${out_file}'

      q_wtime_end = omp_get_wtime()
      call cpu_time(q_cpu_end)
      call SYSTEM_CLOCK(q_sys_end)

      !$OMP CRITICAL
      open(newunit=q_unit,file=
     $q_file,
     $action='write'{file_mode})
      write(q_unit,'(6A, 2I3, 3F24.3)')
     $'<- ', filename, ' ', name, ' ', typ, 
     $th, ths,
     $q_sys_end/cpu_rate, q_cpu_end, q_wtime_end
      close(q_unit)
      !$OMP END CRITICAL
      end subroutine qawa_E

"""
