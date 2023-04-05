abstract class PollingBase {
    backendAddress: string
    responseCallback: (el: any) => void
    pollingInterval: number | boolean = false
    howOftenToPoll: number
    
    constructor(backendAddress: string, responseCallback: (el: any) => void, howOftenToPoll: number = 500) {
        this.backendAddress = backendAddress
        this.responseCallback = responseCallback
        this.howOftenToPoll = howOftenToPoll
    }

    newRequest() {
        if (typeof this.pollingInterval === "boolean") {
            this.pollingInterval = setInterval(this._fetchFromBackend.bind(this), this.howOftenToPoll)
        }
    }
    
    async _fetchFromBackend() {
        try {
            let response = await this._fetchMethod()
            if (response.result == "success") {
                this.responseCallback(response)
                this.clear()
            }
        } catch (err) {
            console.log("Error - PollUntilSuccess")
            console.log(err)
            return
        }
    }

    clear() {
        if (typeof this.pollingInterval === "number") {
            clearInterval(this.pollingInterval)
            this.pollingInterval = false
        }
    }

    abstract _fetchMethod(): { [name: string]: any}
    
}

export class PollUntilSuccessGET extends PollingBase {
    async _fetchMethod() {
        return await fetch(
            this.backendAddress, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
        }).then(response => response.json())
    }
}

export class PollUntilSuccessPOST extends PollingBase {
    body: any
    constructor(backendAddress: string, responseCallback: (el: any) => void, howOftenToPoll: number = 500, body: any) {
        super(backendAddress, responseCallback, howOftenToPoll)
        this.body = body
    }

    async _fetchMethod() {
        return await fetch(
            this.backendAddress, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.body)
        }).then(response => response.json())
    }
}
