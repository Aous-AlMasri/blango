console.log("1. Start");

setTimeout(() => {
  console.log("2. setTimeout");
}, 0);

Promise.resolve().then(() => {
  console.log("3. Promise then");
});

console.log("4. End");
