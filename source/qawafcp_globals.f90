module qawafcp_globals

    use qawafcp_stack
    use qawafcp_history
    implicit none
    logical :: initialized = .false.
    type(Stack), allocatable :: stackArray(:)
    type(History) :: historyObj
    character(:), allocatable :: QAWA_DIR
    integer :: history_batch
    character(100), allocatable :: excludes(:), includes(:)


    contains


    subroutine initialize()

        use omp_lib
        implicit none

        include 'qawa_dir'
        call import_settings()

        allocate(stackArray(omp_get_max_threads()))
        stackArray = Stack(20)

        historyObj = History(100000, history_batch, QAWA_DIR)
        
        initialized = .true.

    end subroutine initialize


    subroutine import_settings()

        use :: json_module
        implicit none
        type(json_file)            :: json
        logical                    :: is_found

        call json%initialize()
    
        call json%load_file(QAWA_DIR // 'settings.json')
        call json%get('history_batch', history_batch, is_found)
        call json%get('excludes', excludes, is_found)
        call json%get('includes', includes, is_found)

        call json%destroy()

    end subroutine import_settings


    function should_process(file_name, procedure_name) result(is_included)
        
        implicit none
        logical :: is_included
        character(*), intent(in) :: file_name, procedure_name
        integer :: i

        is_included = .true.

        do i = 1, size(excludes)
            if(procedure_name == excludes(i) .or. file_name == excludes(i) .or. excludes(i) == "*") then
                is_included = .false.
            endif
        enddo

        if(.not. is_included) then
            do i = 1, size(includes)
                if(procedure_name == includes(i) .or. file_name == includes(i) .or. includes(i) == "*") then
                    is_included = .true.
                endif
            enddo
        endif

        return

    end function should_process


end module qawafcp_globals