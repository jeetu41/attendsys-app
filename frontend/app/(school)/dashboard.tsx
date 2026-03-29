import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAuthStore } from '../../src/store/authStore';

export default function SchoolDashboard() {
  const { user } = useAuthStore();

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.welcomeText}>Welcome, {user?.name}</Text>
        <Text style={styles.roleText}>School Administrator</Text>
      </View>
      <View style={styles.content}>
        <Text style={styles.text}>School Admin Portal</Text>
        <Text style={styles.subtext}>Coming soon...</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#6366f1',
    padding: 24,
    paddingTop: 32,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  roleText: {
    fontSize: 14,
    color: '#fff',
    marginTop: 4,
    opacity: 0.9,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  subtext: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 8,
  },
});
