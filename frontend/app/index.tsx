import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../src/store/authStore';

export default function Index() {
  const router = useRouter();
  const { token, user, checkAuth } = useAuthStore();
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    checkAuth().then(() => {
      setLoading(false);
      if (token && user) {
        // Navigate to appropriate portal based on role
        switch (user.role) {
          case 'platform_admin':
            router.replace('/(admin)/dashboard');
            break;
          case 'school_admin':
            router.replace('/(school)/dashboard');
            break;
          case 'teacher':
            if (user.is_approved) {
              router.replace('/(teacher)/attendance');
            } else {
              router.replace('/pending-approval');
            }
            break;
          case 'parent':
            router.replace('/(parent)/home');
            break;
          default:
            router.replace('/login');
        }
      } else {
        router.replace('/login');
      }
    });
  }, []);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366f1" />
      <Text style={styles.text}>Loading AttendSys...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
  },
  text: {
    marginTop: 16,
    fontSize: 16,
    color: '#64748b',
  },
});
