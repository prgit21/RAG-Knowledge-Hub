import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = 'http://localhost:3000/api'; //change if port number changes

  constructor(private http: HttpClient) {}

  getHelloMessage(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/hello`);
  }

  getProtectedData(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/protected`);
  }
  postLogin(username: string, password: string): Observable<any> {
    const loginData = { username, password };
    const headers = new HttpHeaders({
      'Content-type': 'application/json',
    });
    return this.http.post<any>(`${this.apiUrl}/login`, loginData, { headers });
  }
}
