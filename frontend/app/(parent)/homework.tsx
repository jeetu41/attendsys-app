import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { getAuthHeader, useAuthStore } from '../../src/store/authStore';
import { useBrandingStore } from '../../src/store/brandingStore';

const API_URL = 'https://absence-alert-4.preview.emergentagent.com';

interface Homework {
  _id: string;
  class_name: string;
  subject: string;
  title: string;
  description: string;
  due_date: string;
}

export default function ParentHomeworkScreen() {
  const { user } = useAuthStore();
  const { branding } = useBrandingStore();
  const [homework, setHomework] = useState<Homework[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [studentId, setStudentId] = useState<string | null>(null);

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/parent/children`, { headers });
      if (response.data.length > 0) {
        setStudentId(response.data[0]._id);
        loadHomework(response.data[0]._id);
      }
    } catch (error) {
      console.error('Failed to load children:', error);
    }
  };

  const loadHomework = async (sid: string) => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/parent/homework/${sid}`, { headers });
      setHomework(response.data);
    } catch (error) {
      console.error('Failed to load homework:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    if (studentId) {
      await loadHomework(studentId);
    }
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {homework.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="book-outline" size={64} color="#cbd5e1" />
          <Text style={styles.emptyText}>No homework assigned</Text>
        </View>
      ) : (
        <View style={styles.content}>
          {homework.map((hw) => (
            <View key={hw._id} style={styles.homeworkCard}>
              <View style={styles.homeworkHeader}>
                <View style={[styles.badge, { backgroundColor: branding.primary_color + '20' }]}>
                  <Text style={[styles.badgeText, { color: branding.primary_color }]}>{hw.class_name}</Text>
                </View>
                <Text style={styles.subject}>{hw.subject}</Text>
              </View>

              <Text style={styles.title}>{hw.title}</Text>
              <Text style={styles.description}>{hw.description}</Text>

              <View style={styles.footer}>
                <Ionicons name="calendar-outline" size={16} color="#64748b" />
                <Text style={styles.dateText}>Due: {hw.due_date}</Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 16,
  },
  homeworkCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  homeworkHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  subject: {
    fontSize: 14,
    color: '#64748b',
    fontWeight: '500',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 12,
  },
  dateText: {
    fontSize: 14,
    color: '#64748b',
  },
});
