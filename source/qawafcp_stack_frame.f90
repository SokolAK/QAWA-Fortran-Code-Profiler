module qawafcp_stack_frame

    implicit none

    type, public :: StackFrame
        character(:), allocatable :: name
        double precision :: wtime, ctime, wtimeomp
    end type StackFrame


end module qawafcp_stack_frame