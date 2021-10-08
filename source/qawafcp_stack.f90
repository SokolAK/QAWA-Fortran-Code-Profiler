module qawafcp_stack

    use qawafcp_stack_frame
    implicit none

    type, public :: Stack
        integer :: index
        type(StackFrame), allocatable :: frames(:)
        contains
            procedure :: put => put
            procedure :: pop => pop
            ! procedure :: get_last_frame => get_last_frame
            procedure :: resize => resize
            procedure :: init => init

    end type Stack


    interface Stack
        module procedure constructor
    end interface
    private :: constructor

    
    contains


        function constructor(size) result(new)

            implicit none
            type(Stack) :: new
            integer, intent(in) :: size
            allocate(new%frames(size))

        end function


        subroutine put(this, frame)

            implicit none
            class(Stack) :: this
            type(StackFrame) :: frame

            !$OMP CRITICAL
            this%index = this%index + 1
            if(this%index > size(this%frames)) call this%resize()
            this%frames(this%index) = frame
            !$OMP END CRITICAL
            
        end subroutine put


        function pop(this) result(frame)

            implicit none
            class(Stack) :: this
            type(StackFrame) :: frame

            !$OMP CRITICAL
            frame = this%frames(this%index)
            this%index = this%index - 1
            !$OMP END CRITICAL
            
        end function pop


        subroutine resize(this)
            
            implicit none
            class(Stack) :: this
            type(StackFrame), allocatable :: temp(:)
            allocate(temp(size(this%frames)*2))
            temp(:size(this%frames)) = this%frames
            call move_alloc(temp,this%frames)

        end subroutine resize


        subroutine init(this)

            implicit none
            class(Stack) :: this
            allocate(this%frames(10))

        end subroutine init


end module qawafcp_stack