import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyDataAccessComponent } from './jrny-data-access.component';

describe('JrnyDataAccessComponent', () => {
  let component: JrnyDataAccessComponent;
  let fixture: ComponentFixture<JrnyDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
