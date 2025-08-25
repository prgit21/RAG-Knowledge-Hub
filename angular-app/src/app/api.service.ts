import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getHelloMessage(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/hello`);
  }

  getProtectedData(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/protected`);
  }
  postLogin(username: string, password: string): Observable<any> {
  const body = new HttpParams()
    .set('username', username)
    .set('password', password);

  const headers = new HttpHeaders({
    'Content-Type': 'application/x-www-form-urlencoded'
  });

  // Pass the URL-encoded string
  return this.http.post(`${this.apiUrl}/login`, body.toString(), { headers });
}

}
