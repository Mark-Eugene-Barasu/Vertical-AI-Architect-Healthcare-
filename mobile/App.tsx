import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Amplify } from "aws-amplify";
import LoginScreen from "./src/screens/LoginScreen";
import NoteScreen from "./src/screens/NoteScreen";
import DrugScreen from "./src/screens/DrugScreen";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: process.env.EXPO_PUBLIC_COGNITO_USER_POOL_ID!,
      userPoolClientId: process.env.EXPO_PUBLIC_COGNITO_CLIENT_ID!,
    },
  },
});

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator screenOptions={{ tabBarActiveTintColor: "#2b6cb0", headerShown: false }}>
      <Tab.Screen name="Notes"  component={NoteScreen}  options={{ tabBarLabel: "🎙️ Notes" }} />
      <Tab.Screen name="Drugs"  component={DrugScreen}  options={{ tabBarLabel: "💊 Drugs" }} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Main"  component={MainTabs} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
