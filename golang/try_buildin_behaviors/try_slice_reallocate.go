/*
conlusion:
  slice is reallocated when necessary
  memory sharing/non-sharing are unguaranteed between too slices
	one is base on another
*/
package main

import (
	"fmt"
)

func testSliceReallocation(capability int) {
	var a []int = make([]int, 3, capability)
	for n := 0; n < 3; n++ {
		a[n] = n + 1
	}
	b := append(a, 4)
	b[1] *= -1
	if b[1] == a[1] {
		fmt.Println("The two slices share memory")
	} else {
		fmt.Println("The two slices do NOT share memory")
	}
}

func testSlicing() {
	var x []int = make([]int, 1, 3)
	x[0] = 1
	var y = x[1:]
	var z = append(y, 7)
	x = append(x, 6)
	if z[0] != 7 {
		fmt.Println("sharing memory: z is re-write by x")
	} else {
		fmt.Println("No-sharing memory")
	}
}

func main() {
	testSliceReallocation(3)
	testSliceReallocation(4)
	testSlicing()
}
