subroutine qawafcp_start(file_name, procedure_name, procedure_type)

    use qawafcp_globals
    use qawafcp_stack_frame
    use omp_lib
    implicit none
    character(*), intent(in) :: file_name, procedure_name, procedure_type
    double precision :: ctime, wtime
    type(StackFrame) :: frame
    integer :: thread_id, max_threads
    character(:), allocatable :: full_name
    character(200) :: history_log
    integer :: count, count_rate, count_max, i
    logical :: should_profile

    ! if(.not. initialized) call initialize()

    ! should_profile = should_process(file_name, procedure_name)

    ! if(should_profile) then
    !     call system_clock(count, count_rate, count_max)
    !     wtime = count / real(count_rate)

    !     thread_id = OMP_GET_THREAD_NUM() + 1
    !     max_threads = OMP_GET_NUM_THREADS()

    !     call cpu_time(ctime)
    !     full_name = file_name // ' ' // procedure_name // ' ' // procedure_type
    !     frame = StackFrame(full_name, wtime, ctime, omp_get_wtime())
    !     call stackArray(thread_id)%put(frame)

    !     write(history_log, *) '-> ', trim(full_name), ' ', thread_id, ' ', max_threads
    !     call historyObj%add(trim(history_log))
    ! endif



end subroutine qawafcp_start


subroutine qawafcp_end(file_name, procedure_name, procedure_type)

    use qawafcp_globals
    use qawafcp_stack_frame
    use omp_lib
    implicit none
    character(*), intent(in) :: file_name, procedure_name, procedure_type
    double precision :: ctime, wtime
    type(StackFrame) :: frame
    integer :: thread_id, max_threads
    character(200) :: history_log
    integer :: count, count_rate, count_max, i
    logical :: should_profile

    ! should_profile = should_process(file_name, procedure_name)

    ! if(should_profile) then
    !     call system_clock(count, count_rate, count_max)
    !     wtime = count / real(count_rate)

    !     thread_id = OMP_GET_THREAD_NUM() + 1
    !     max_threads = OMP_GET_NUM_THREADS()

    !     call cpu_time(ctime)
    !     frame = stackArray(thread_id)%pop()
    !     frame%wtime = wtime - frame%wtime
    !     frame%ctime = ctime - frame%ctime
    !     frame%wtimeomp = omp_get_wtime() - frame%wtimeomp

    !     write(history_log, *) '<- ', trim(frame%name), ' ', &
    !         thread_id, ' ', max_threads, ' ', &
    !         frame%wtime, ' ', frame%ctime, ' ', frame%wtimeomp
    !     call historyObj%add(trim(history_log))
    ! endif

end subroutine qawafcp_end