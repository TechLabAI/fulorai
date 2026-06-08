import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JrnyAccessComponent } from './jrny-access.component';

describe('JrnyAccessComponent', () => {
  let component: JrnyAccessComponent;
  let fixture: ComponentFixture<JrnyAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JrnyAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(JrnyAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
