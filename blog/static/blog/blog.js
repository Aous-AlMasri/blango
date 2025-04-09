class Greeter {
  constructor (name) {
    this.name = name
  }

  getGreeting() {
    if (this.name === undefined) {
      return 'hello, no name'
    }
    return 'hello, ' + this.name
  }

  showGreeting (greetMessage) {
    console.log(greetMessage)
  }

  greet() {
    this.showGreeting(this.getGreeting())
  }
}

class DelayedGreeter extends Greeter {
  delay = 2000

  constructor (name, delay) {
    super(name)
    if (delay !== undefined) {
      this.delay = delay
    }
  }

  greet () {
    setTimeout(() => {
      this.showGreeting(this.getGreeting())
    }, this.delay)
  }
}

const dg1 = new DelayedGreeter('aous', 6000)

dg1.greet()

const dg2 = new DelayedGreeter('omar')

dg2.greet()
