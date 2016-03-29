package main

import (
	"fmt"
)

func fooFunc(x int) int {
	return x+1
}

type Foo struct {
	x, y int64
}

type CompositeSlice struct {
	x int
	s []int
}

func (*Foo) Error() string {
	return "Foo"
}

func main() {
	fmt.Println("func-nil", fooFunc == nil)
	// fmt.Println("func-func", fooFunc == fooFunc) // compile error

	var interface1 interface{} = &Foo{1, 2}
	var valueFoo = Foo{1, 2}
	var interface2 interface{} = &valueFoo
	var interface3 interface{} = &valueFoo
	fmt.Println("interface-nil", interface1 == nil)
	fmt.Println("interface-interface", interface1 == interface2)
	fmt.Println("interface-interface", interface2 == interface3)

	var valueInterface1 interface{} = Foo{2, 1}
	var valueInterface2 interface{} = Foo{2, 1}
	fmt.Println("value_interface-nil", valueInterface1 == nil)
	fmt.Println("value_interface-interface", valueInterface1 == valueInterface2)

	var foo1 = &Foo{2, 1}
	var foo2 = &Foo{2, 1}
	fmt.Println("pointer-nil", foo1 == nil, foo2==nil)
	fmt.Println("pointer-pointer", foo1 == foo2)

	var slice1 = []int64 {12}
	var slice2 = []int64 {1}
	fmt.Println("slice-nil", slice1 == nil, slice2 == nil)
	// fmt.Println("slice-slice", slice1 == slice2) // compile error

	var map1 = map[int]int{1:2}
	var map2 = map[int]int{1:2}
	fmt.Println("map-nil", map1==nil, map2==nil)
	// fmt.Println("map-map", map1==map2) // compile error

	var c1 chan int = make(chan int)
	var c2 = c1
	fmt.Println("chan-nil", c1 == nil)
	fmt.Println("chan-chan", c1 == c2)

	// fmt.Println("string-nil", "abc" == nil) // complie error
	fmt.Println("string-string", "abc" == "abc")

	// fmt.Println("array-nil", [3]int{1, 2, 3} == nil) // complie error
	fmt.Println("array-array", [3]int{1, 2, 3} == [3]int{1, 2, 3})

	// fmt.Println("struct-nil", Foo{2, 1} == nil) // complie error
	fmt.Println("struct-struct", Foo{2, 1} == Foo{2, 1})

	// fmt.Println("comp-slice", CompositeSlice{7, []int{1, 2}} == CompositeSlice{7, []int{1, 2}})
}
