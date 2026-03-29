import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SchoolTeachersScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Manage Teachers</Text>
      <Text style={styles.subtext}>Coming soon...</Text>
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
