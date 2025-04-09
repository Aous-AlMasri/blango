const numbers = [0,2,3,4,5,7,8,9]

numbers.forEach((value => {
  console.log(value)
}))


const doubled = numbers.map(value => value * 2)

console.log(doubled)