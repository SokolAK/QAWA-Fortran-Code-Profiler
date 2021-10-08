module qawafcp_history

    implicit none

    type, public :: History
        integer :: index = 0, dump_index = 0
        integer :: batch = 1
        character(200), allocatable :: logs(:)
        character(200) :: dump_path
        contains
            procedure :: add => add
            procedure :: resize => resize
            procedure :: dump => dump
    end type History

    interface History
        module procedure constructor
    end interface
    private :: constructor


    contains


        function constructor(size, batch, dump_path) result(new)

            implicit none
            type(History) :: new
            integer, intent(in) :: size, batch
            character(*) :: dump_path


            allocate(new%logs(size))
            new%batch = batch
            new%dump_path = trim(dump_path) // '/outs/qawa.out'

        end function


        subroutine add(this, log)

            implicit none
            class(History) :: this
            character(*) :: log

            !$OMP CRITICAL
            this%index = this%index + 1
            if(this%index > size(this%logs)) call this%resize()
            this%logs(this%index) = log
            !$OMP END CRITICAL

            if(this%batch > 0) then
                if(modulo(this%index, this%batch) == 0) then
                    call this%dump()
                endif
            endif

            if(index(log, '<-') /= 0 .and. index(log, 'MAIN') /= 0) then
                call this%dump()
            endif
            
        end subroutine add


        subroutine resize(this)
            
            implicit none
            class(History) :: this
            character(200), allocatable :: temp(:)
            allocate(temp(size(this%logs)*2))
            temp(:size(this%logs)) = this%logs
            call move_alloc(temp,this%logs)

        end subroutine resize


        subroutine dump(this)

            implicit none
            class(History) :: this
            integer :: q_unit, i

            !$OMP CRITICAL
            if(this%index > this%batch .and. this%batch > 0) then
                open(newunit=q_unit,file=this%dump_path,action='write',position='append')
            else
                open(newunit=q_unit,file=this%dump_path,action='write')
            endif

            do i = this%dump_index + 1, this%index
                write(q_unit, '(a)', advance='no') this%logs(i)
                write(q_unit, '(a)') ''
            enddo
            close(q_unit)
            !$OMP END CRITICAL

            this%dump_index = this%index

        end subroutine dump


end module qawafcp_history