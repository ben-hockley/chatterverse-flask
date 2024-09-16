const ProgressColours = ['darkred', 'red', 'orange', 'yellow', 'blue', 'green', 'darkgreen']

function PasswordStrength() {
    const password = document.getElementById('password').value

    let rating = 0;
    if (password.length > 5){
        rating++;
    }
    if (password.length > 8) {
        rating++;
    }
    //check if password contains lower case letter
    if (password.match(/[a-z]/)) {
        rating++;
    }
    //check if password contains upper case letter
    if (password.match(/[A-Z]/)) {
        rating++;
    }
    //check if password contains number
    if (password.match(/[0-9]/)) {
        rating++;
    }
    //check if password contains special character
    if (password.match(/[^a-zA-Z0-9]/)) {
        rating++;
    }

    let progressColor = ProgressColours[rating]
    console.log(progressColor)

    let barStyle = {
        backgroundColor: progressColor,
        width: '100%'
    };

    return (
        <>
            <label for="passwordStrengthBar" className="form-label">Password Strength:</label>
            <progress value={rating} max="6" id="passwordStrengthBar" name="passwordStrengthBar" style={barStyle}></progress>
        </>
    )
}

function getPasswordStrength() {
    ReactDOM.render(<PasswordStrength/>, document.getElementById('passwordStrength'))
}