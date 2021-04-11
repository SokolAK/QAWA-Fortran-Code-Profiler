Subroutine sub1(x, y, z)
    use module
    integer :: i 
    <some code>
End subroutine sub1

Subroutine sub2 &
    (x, y, z)
    use module
    real :: r
    <some code>
End subroutine

subroutine sub3&
    (x, y, z)
    real :: r
    <some code>
end

subroutine not_sub1(x,y)
    <some code>
end


function fun1(x) result(y)
integer :: j
real :: y
<some code>
return
end

REAL*8 Function fun2(x)
integer :: j
<some code>
Return
End function fun2

function not_fun1(x) result(y)
<some code>
end function