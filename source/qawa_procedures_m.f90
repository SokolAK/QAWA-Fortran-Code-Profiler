module qawa_procedures_m

    use omp_lib
    ! use qawa_dictionary_m

    private

    type, public :: Qawa
        ! private
        ! integer :: sys_start, sys_end
        ! real(kind=8) :: wtime_start, wtime_end, cpu_start, cpu_end
        ! real(kind=8) :: cpu_rate
        ! character(256) :: path
        ! integer :: th, ths, count_rate, count_max, unit
        ! double precision, allocatable :: A0(:)
        contains
            procedure :: test => qawa_test
            ! procedure :: start_block => start_block
            ! procedure :: end_block   => end_block
    end type Qawa


    contains

    subroutine qawa_test(this)
        implicit none
        class(Qawa) :: this
        ! type(dictionary_t) :: d
        ! call d%set('pi', '3.14159')
        ! write(*,*) 'pi', ' = ', d%get('pi')
        print*, "ELO ELO ELO"
    end subroutine qawa_test


    ! subroutine start_block(this, outfile)
    
    !     implicit none
    !     class(Qawa) :: this
    !     character(256), intent(in) :: outfile
    !     integer :: unit

    !     this%path = outfile

    !     call system_clock(count_rate=this%count_rate)
    !     call system_clock(count_max=this%count_max)
    !     this%cpu_rate = real(this%count_rate)
    !     this%th = OMP_GET_THREAD_NUM() + 1
    !     this%ths = OMP_GET_NUM_THREADS()

    !     this%wtime_start = omp_get_wtime()
    !     call cpu_time(this%cpu_start)
    !     call system_clock(this%sys_start)
  
    !     !$OMP CRITICAL
    !     open(newunit=unit, file=this%path, action='write', position='append')
    !         write(unit,'(A, 2I3)') '-> {file} {name} {typ}', this%th, this%ths
    !     close(unit)
    !     !$OMP END CRITICAL

    ! end subroutine start_block


    ! subroutine end_block(this)
    
    !     implicit none
    !     class(Qawa) :: this
    !     integer :: unit

    !     this%wtime_end = omp_get_wtime()
    !     call cpu_time(this%cpu_end)
    !     call SYSTEM_CLOCK(this%sys_end)
        
    !     !$OMP CRITICAL
    !     open(newunit=unit, file=this%path, action='write', position='append')
    !         write(unit,'(A, 2I3, 3F14.6)')'<- {file} {name} {typ}', &
    !         this%th, this%ths, (this%sys_end-this%sys_start)/this%cpu_rate, &
    !         this%cpu_end-this%cpu_start, this%wtime_end-this%wtime_start
    !     close(unit)
    !     !$OMP END CRITICAL

    ! end subroutine end_block


end module qawa_procedures_m