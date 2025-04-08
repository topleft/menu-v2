import { BrowserRouter as Router } from 'react-router-dom'
import { Authenticator } from '@aws-amplify/ui-react'
import '@aws-amplify/ui-react/styles.css'

function App() {
  return (
    <Authenticator hideSignUp>
      {({ signOut, user }) => (
        <Router>
          <div>
            <h1>Welcome {user?.username}</h1>
            <button onClick={signOut}>Sign out</button>
          </div>
        </Router>
      )}
    </Authenticator>
  )
}

export default App
