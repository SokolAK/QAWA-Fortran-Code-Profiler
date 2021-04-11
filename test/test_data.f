      SUBROUTINE sub1
     $(x, y, z)
      use module
      integer :: i 
      <some code>
      END

      SUBROUTINE sub2
     $(x, y, z)
C comment
      integer :: i 
      <some code>
      END SUBROUTINE
      
      subroutine not_sub1(x,y)
      <some code>
      end

      
      FUNCTION fun1(x) result(y)
      integer :: j
      real :: y
      <some code>
      RETURN
      END

      REAL*8 FUNCTION fun2(x)
      integer :: j
      <some code>
      RETURN
      END FUNCTION fun2

      function not_fun1(x) result(y)
      <some code>
      end function