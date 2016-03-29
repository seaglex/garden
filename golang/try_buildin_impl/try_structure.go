package main

import (
	"fmt"
	"unsafe"
	"reflect"
)

type MyInt byte

func (this *MyInt) Error() string {
	if this != nil {
		return fmt.Sprintf("<MyInt:%d>", *this)
	} else {
		return "<MyInt:nil>"
	}
}
func (this *MyInt) Plus() int {
	return (int)(*this)
}

type FooXY struct {
	x int
	y int
}
type ValueFooXY struct {
	x int
	y int
}
func (this *FooXY) Error() string {
	return fmt.Sprintf("<FooXY> x=%d y=%d", this.x, this.y)
}
func (this *FooXY) Plus() int {
	if this == nil {
		return 0
	}
	return this.x + this.y
}
func (this ValueFooXY) Plus() int {
	return this.x + this.y
}
func (this ValueFooXY) Error() string {
	return fmt.Sprintf("<ValueFooXY> x=%d y=%d", this.x, this.y)
}
func XYPlus(self *FooXY) int {
	if self == nil {
		return 0
	}
	return self.x + self.y
}


func TestInterface(x error, isPrintHeader bool) {
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "interface-int1", "interface-int2", "interface-int3")
	}
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	var ptr2 *int64 = (*int64)(unsafe.Pointer((uintptr(unsafe.Pointer(&x))+8)))
	var ptr3 *int64 = (*int64)(unsafe.Pointer((uintptr(unsafe.Pointer(&x))+16)))
	fmt.Println(x, uintptr(unsafe.Pointer(&x)), x == nil, *ptr1, *ptr2, *ptr3)
}

func TestSlice(x []int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	var ptr2 *int64 = (*int64)(unsafe.Pointer((uintptr(unsafe.Pointer(&x))+8)))
	var ptr3 *int64 = (*int64)(unsafe.Pointer((uintptr(unsafe.Pointer(&x))+16)))
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "slice-int1", "slice-int2", "slice-int3")
	}
	fmt.Println(x, uintptr(unsafe.Pointer(&x)), x == nil, *ptr1, *ptr2, *ptr3)
	// fmt.Println(x==x) // compile error
}

func TestMap(x map[int]int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "map-int1")
	}
	fmt.Println(x, uintptr(unsafe.Pointer(&x)), x == nil, *ptr1)
}

func TestFunc(x func(*FooXY) int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	var ref1, ref2 *int64
	var ref2ref *int64
	if *ptr1 != 0 {
		ref1 = (*int64)(unsafe.Pointer(uintptr(*ptr1)))
		ref2 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 8))
		ref2ref = (*int64)(unsafe.Pointer(uintptr(*ref2)))
		fmt.Println(reflect.TypeOf(unsafe.Pointer(ref2ref)))
	} else {
		var zero int64 = 0
		ref1 = &zero
		ref2 = &zero
		ref2ref = &zero
	}
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "func-int1", "func-ref1", "func-ref2", "func-ref2ref")
	}
	fmt.Println(x, uintptr(unsafe.Pointer(&x)), x == nil, *ptr1, *ref1, *ref2, *ref2ref)
	// fmt.Println("func(1) = ", x(1))
}

func TestMemberFunc(f func()int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&f))
	var ref1, ref2 *int64
	var ref2ref *int64
	if *ptr1 != 0 {
		ref1 = (*int64)(unsafe.Pointer(uintptr(*ptr1)))
		ref2 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 8))
		ref2ref = (*int64)(unsafe.Pointer(uintptr(*ref2)))
		fmt.Println(reflect.TypeOf(unsafe.Pointer(ref2ref)))
	} else {
		var zero int64 = 0
		ref1 = &zero
		ref2 = &zero
		ref2ref = &zero
	}
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "mfunc-int1", "mfunc-ref1", "mfunc-ref2", "mfun-ref2ref")
	}
	fmt.Println(f, uintptr(unsafe.Pointer(&f)), f == nil, *ptr1, *ref1, *ref2, *ref2ref)
}

func TestValueMemberFunc(f func()int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&f))
	var ref1, ref2, ref3, ref4, ref5 *int64
	if *ptr1 != 0 {
		ref1 = (*int64)(unsafe.Pointer(uintptr(*ptr1)))
		ref2 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 8))
		ref3 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 16))
		ref4 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 24))
		ref5 = (*int64)(unsafe.Pointer(uintptr(*ptr1) + 32))
	} else {
		var zero int64 = 0
		ref1 = &zero
		ref2 = &zero
		ref3 = &zero
		ref4 = &zero
		ref5 = &zero
	}
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "mfunc-int1", "mfunc-ref1", "mfunc-ref2", "mfun-ref3", "mfun-ref4", "mfun-ref5" )
	}
	fmt.Println(f, uintptr(unsafe.Pointer(&f)), f == nil, *ptr1, *ref1, *ref2, *ref3, *ref4, *ref5)
}


func TestPointer(x *int, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	if isPrintHeader {
		fmt.Println("value", "addr", "equal(nil)", "pointer-int1")
	}
	fmt.Println(x, uintptr(unsafe.Pointer(x)), x == nil, *ptr1)
}

func TestString(x string, isPrintHeader bool) {
	var ptr1 *int64 = (*int64)(unsafe.Pointer(&x))
	var ptr2 *int64 = (*int64)(unsafe.Pointer((uintptr(unsafe.Pointer(&x))+8)))
	if isPrintHeader {
		fmt.Println("value", "addr", "string-int1", "string-int2")
	}
	fmt.Println(x, uintptr(unsafe.Pointer(&x)), *ptr1, *ptr2)
	// x == nil: compile error
}


func main() {
	var myInt MyInt = MyInt(1)
	var xy = &FooXY{37, 2}
	var xyValue = ValueFooXY{47, 2}

	fmt.Println("## Test func")
	fmt.Println("original func/func-size", XYPlus, unsafe.Sizeof(XYPlus))
	fmt.Println("original func/func-size", (*FooXY).Plus, unsafe.Sizeof((*FooXY).Plus))
	TestFunc(XYPlus, true)
	TestFunc((*FooXY).Plus, false)
	TestFunc((func(*FooXY) int)(nil), false)
	TestFunc(nil, false)

	fmt.Println("## Test member-func")
	var mi *MyInt = &myInt
	TestMemberFunc(mi.Plus, true)
	fmt.Println("original addr/func/func-size", uintptr(unsafe.Pointer(xy)), xy.Plus, unsafe.Sizeof(xy.Plus))
	TestMemberFunc(xy.Plus, true)
	TestMemberFunc(nil, false)

	fmt.Println("## Test value member-func")
	TestValueMemberFunc(xyValue.Plus, true)
	TestValueMemberFunc(nil, false)

	fmt.Println("## Test interface error")
	fmt.Println("original addr", uintptr(unsafe.Pointer(&myInt)))
	fmt.Println("original addr", uintptr(unsafe.Pointer(xy)))
	TestInterface(&myInt, true)
	TestInterface((*MyInt)(nil), false)
	TestInterface(xy, false)
	TestInterface(xyValue, false)
	TestInterface(nil, false)

	fmt.Println("## Test pointer")
	var i int = 1
	fmt.Println("original addr", uintptr(unsafe.Pointer(&i)))
	TestPointer(&i, true)
	TestPointer((*int)(nil), false)
	TestPointer(nil, false)

	fmt.Println("## Test slice")
	var slice1 = make([]int, 1, 7)
	slice1[0] = 1
	var slice0 = []int{}
	var slicenil = ([]int)(nil)
	TestSlice(slice1, true)
	TestSlice(slice1[1:], false)
	TestSlice(append(slice1, 0), false)
	TestSlice(slice0, false)
	TestSlice(append(slice0, 0), false)
	TestSlice(slicenil, false)
	TestSlice(append(slicenil, 0), false)
	TestSlice(nil, false)

	fmt.Println("## Test Map")
	var map1 = map[int]int{1: 2}
	TestMap(map1, true)
	map1[2] = 3
	TestMap(map1, false)
	TestMap(map[int]int{}, false)
	TestMap((map[int]int)(nil), false)
	TestMap(nil, false)

	fmt.Println("## Test string")
	var s1 = "abc"
	var s2 = "abcd"
	TestString(s1, true)
	TestString(s2, false)
	TestString("", false)
	// TestString(s2, false) # compile error
}